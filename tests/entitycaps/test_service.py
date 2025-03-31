########################################################################
# File name: test_service.py
# This file is part of: aioxmpp
#
# LICENSE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
########################################################################
import asyncio
import contextlib
import io
import pathlib
import tempfile
import unittest
import unittest.mock

import aioxmpp.disco as disco
import aioxmpp.service as service
import aioxmpp.stanza as stanza
import aioxmpp.structs as structs
import aioxmpp.xml

from aioxmpp.utils import namespaces

import aioxmpp.entitycaps.service as entitycaps_service

from aioxmpp.testutils import (
    make_connected_client,
    CoroutineMock,
    run_coroutine,
)


TEST_FROM = structs.JID.fromstr("foo@bar.example/r1")


_src = io.BytesIO(b"""\
<?xml version="1.0" ?><query node="http://tkabber.jabber.ru/#+0mnUAF1ozCEc37cm\
dPPsYbsfhg=" xmlns="http://jabber.org/protocol/disco#info"><identity category=\
"client" name="Tkabber" type="pc"/><feature var="games:board"/><feature var="h\
ttp://jabber.org/protocol/activity"/><feature var="http://jabber.org/protocol/\
activity+notify"/><feature var="http://jabber.org/protocol/bytestreams"/><feat\
ure var="http://jabber.org/protocol/chatstates"/><feature var="http://jabber.o\
rg/protocol/commands"/><feature var="http://jabber.org/protocol/disco#info"/><\
feature var="http://jabber.org/protocol/disco#items"/><feature var="http://jab\
ber.org/protocol/geoloc"/><feature var="http://jabber.org/protocol/geoloc+noti\
fy"/><feature var="http://jabber.org/protocol/ibb"/><feature var="http://jabbe\
r.org/protocol/iqibb"/><feature var="http://jabber.org/protocol/mood"/><featur\
e var="http://jabber.org/protocol/mood+notify"/><feature var="http://jabber.or\
g/protocol/rosterx"/><feature var="http://jabber.org/protocol/si"/><feature va\
r="http://jabber.org/protocol/si/profile/file-transfer"/><feature var="http://\
jabber.org/protocol/tune"/><feature var="jabber:iq:avatar"/><feature var="jabb\
er:iq:browse"/><feature var="jabber:iq:last"/><feature var="jabber:iq:oob"/><f\
eature var="jabber:iq:privacy"/><feature var="jabber:iq:roster"/><feature var=\
"jabber:iq:time"/><feature var="jabber:iq:version"/><feature var="jabber:x:dat\
a"/><feature var="jabber:x:event"/><feature var="jabber:x:oob"/><feature var="\
urn:xmpp:ping"/><feature var="urn:xmpp:time"/><x type="result" xmlns="jabber:x\
:data"><field type="hidden" var="FORM_TYPE"><value>urn:xmpp:dataforms:software\
info</value></field><field var="software"><value>Tkabber</value></field><field\
 var="software_version"><value>1.0-svn-20140122 (Tcl/Tk 8.4.20)</value></field\
><field var="os"><value>FreeBSD</value></field><field var="os_version"><value>\
10.0-STABLE</value></field></x></query>""")
TEST_DB_ENTRY = aioxmpp.xml.read_single_xso(_src, disco.xso.InfoQuery)
TEST_DB_ENTRY_VER = "+0mnUAF1ozCEc37cmdPPsYbsfhg="
TEST_DB_ENTRY_HASH = "sha-1"
TEST_DB_ENTRY_NODE_BARE = "http://tkabber.jabber.ru/"


class TestCache(unittest.TestCase):
    def setUp(self):
        self.c = entitycaps_service.Cache()

    def tearDown(self):
        del self.c

    def test_lookup_in_database_key_errors_if_no_such_entry(self):
        key = unittest.mock.Mock()
        with self.assertRaises(KeyError):
            self.c.lookup_in_database(key)

    def test_system_db_path_used_in_lookup(self):
        base = unittest.mock.Mock()
        base.p = unittest.mock.MagicMock()
        self.c.set_system_db_path(base.p)

        with contextlib.ExitStack() as stack:
            stack.enter_context(unittest.mock.patch(
                "aioxmpp.xml.read_single_xso",
                new=base.read_single_xso
            ))

            result = self.c.lookup_in_database(base.key)

        calls = list(base.mock_calls)
        self.assertSequenceEqual(
            calls,
            [
                unittest.mock.call.p.__truediv__(base.key.path),
                unittest.mock.call.p.__truediv__().open("rb"),
                unittest.mock.call.p.__truediv__().open().__enter__(),
                unittest.mock.call.read_single_xso(
                    base.p.__truediv__().open(),
                    disco.xso.InfoQuery,
                ),
                unittest.mock.call.p.__truediv__().open().__exit__(
                    None, None, None
                ),
            ]
        )

        self.assertEqual(
            result,
            base.read_single_xso()
        )

    def test_user_db_path_used_in_lookup_as_fallback(self):
        base = unittest.mock.Mock()
        base.p = unittest.mock.MagicMock()
        base.userp = unittest.mock.MagicMock()
        self.c.set_system_db_path(base.p)
        self.c.set_user_db_path(base.userp)

        base.p.__truediv__().open.side_effect = FileNotFoundError()
        base.mock_calls.clear()

        with contextlib.ExitStack() as stack:
            stack.enter_context(unittest.mock.patch(
                "aioxmpp.xml.read_single_xso",
                new=base.read_single_xso
            ))

            result = self.c.lookup_in_database(base.key)

        calls = list(base.mock_calls)
        self.assertSequenceEqual(
            calls,
            [
                unittest.mock.call.p.__truediv__(base.key.path),
                unittest.mock.call.p.__truediv__().open("rb"),
                unittest.mock.call.userp.__truediv__(base.key.path),
                unittest.mock.call.userp.__truediv__().open("rb"),
                unittest.mock.call.userp.__truediv__().open().__enter__(),
                unittest.mock.call.read_single_xso(
                    base.userp.__truediv__().open(),
                    disco.xso.InfoQuery,
                ),
                unittest.mock.call.userp.__truediv__().open().__exit__(
                    None, None, None
                ),
            ]
        )

        self.assertEqual(
            result,
            base.read_single_xso()
        )

    def test_user_db_path_used_if_system_db_is_unset(self):
        base = unittest.mock.Mock()
        base.p = unittest.mock.MagicMock()
        base.userp = unittest.mock.MagicMock()
        self.c.set_user_db_path(base.userp)

        with contextlib.ExitStack() as stack:
            stack.enter_context(unittest.mock.patch(
                "aioxmpp.xml.read_single_xso",
                new=base.read_single_xso
            ))

            result = self.c.lookup_in_database(base.key)
        calls = list(base.mock_calls)
        self.assertSequenceEqual(
            calls,
            [
                unittest.mock.call.userp.__truediv__(base.key.path),
                unittest.mock.call.userp.__truediv__().open("rb"),
                unittest.mock.call.userp.__truediv__().open().__enter__(),
                unittest.mock.call.read_single_xso(
                    base.userp.__truediv__().open(),
                    disco.xso.InfoQuery,
                ),
                unittest.mock.call.userp.__truediv__().open().__exit__(
                    None, None, None
                ),
            ]
        )

        self.assertEqual(
            result,
            base.read_single_xso()
        )

    def test_lookup_uses_lookup_in_database(self):
        with unittest.mock.patch.object(
                self.c,
                "lookup_in_database") as lookup_in_database:
            result = run_coroutine(self.c.lookup(unittest.mock.sentinel.key))

        lookup_in_database.assert_called_with(unittest.mock.sentinel.key)
        self.assertEqual(result, lookup_in_database())

    def test_create_query_future_used_by_lookup(self):
        fut = asyncio.Future()

        base = unittest.mock.Mock()
        with contextlib.ExitStack() as stack:
            stack.enter_context(unittest.mock.patch(
                "asyncio.Future",
                new=base.Future
            ))

            stack.enter_context(unittest.mock.patch.object(
                self.c,
                "lookup_in_database",
                new=base.lookup_in_database
            ))

            base.lookup_in_database.side_effect = KeyError()
            base.Future.return_value = fut

            self.assertIs(
                self.c.create_query_future(unittest.mock.sentinel.key),
                fut,
            )

            task = asyncio.ensure_future(
                self.c.lookup(unittest.mock.sentinel.key)
            )
            run_coroutine(asyncio.sleep(0))

            self.assertFalse(task.done())

            fut.set_result(unittest.mock.sentinel.result)

            run_coroutine(asyncio.sleep(0))

            self.assertIs(task.result(), unittest.mock.sentinel.result)

    def test_lookup_key_errors_if_no_matching_entry_or_future(self):
        fut = asyncio.Future()

        base = unittest.mock.Mock()
        with contextlib.ExitStack() as stack:
            stack.enter_context(unittest.mock.patch(
                "asyncio.Future",
                new=base.Future
            ))

            stack.enter_context(unittest.mock.patch.object(
                self.c,
                "lookup_in_database",
                new=base.lookup_in_database
            ))

            base.lookup_in_database.side_effect = KeyError()
            base.Future.return_value = fut

            self.assertIs(
                self.c.create_query_future(unittest.mock.sentinel.key),
                fut,
            )

            with self.assertRaises(KeyError):
                run_coroutine(self.c.lookup(unittest.mock.sentinel.other_key))

    def test_lookup_loops_on_query_futures(self):
        fut1 = asyncio.Future()
        fut2 = asyncio.Future()
        fut3 = asyncio.Future()

        base = unittest.mock.Mock()
        with contextlib.ExitStack() as stack:
            stack.enter_context(unittest.mock.patch(
                "asyncio.Future",
                new=base.Future
            ))

            stack.enter_context(unittest.mock.patch.object(
                self.c,
                "lookup_in_database",
                new=base.lookup_in_database
            ))

            base.lookup_in_database.side_effect = KeyError()
            base.Future.return_value = fut1
            self.c.create_query_future(unittest.mock.sentinel.key)

            task = asyncio.ensure_future(
                self.c.lookup(unittest.mock.sentinel.key)
            )
            run_coroutine(asyncio.sleep(0))

            self.assertFalse(task.done())

            fut1.set_exception(ValueError())

            base.Future.return_value = fut2
            self.c.create_query_future(unittest.mock.sentinel.key)

            run_coroutine(asyncio.sleep(0))

            self.assertFalse(task.done())

            fut2.set_exception(ValueError())

            base.Future.return_value = fut3
            self.c.create_query_future(unittest.mock.sentinel.key)

            run_coroutine(asyncio.sleep(0))

            self.assertFalse(task.done())

            fut3.set_result(base.result)

            run_coroutine(asyncio.sleep(0))

            self.assertIs(task.result(), base.result)

    def test_lookup_key_errors_if_last_query_future_fails(self):
        fut = asyncio.Future()

        base = unittest.mock.Mock()
        with contextlib.ExitStack() as stack:
            stack.enter_context(unittest.mock.patch(
                "asyncio.Future",
                new=base.Future
            ))

            stack.enter_context(unittest.mock.patch.object(
                self.c,
                "lookup_in_database",
                new=base.lookup_in_database
            ))

            base.lookup_in_database.side_effect = KeyError()
            base.Future.return_value = fut

            self.assertIs(
                self.c.create_query_future(unittest.mock.sentinel.key),
                fut,
            )

            task = asyncio.ensure_future(
                self.c.lookup(unittest.mock.sentinel.key)
            )
            run_coroutine(asyncio.sleep(0))

            self.assertFalse(task.done())

            fut.set_exception(ValueError())

            run_coroutine(asyncio.sleep(0))

            with self.assertRaises(KeyError):
                run_coroutine(task)

    def test_add_cache_entry_is_immediately_visible_in_lookup_and_defers_writeback(self):  # NOQA
        q = disco.xso.InfoQuery()
        p = unittest.mock.MagicMock()
        key = unittest.mock.Mock()
        self.c.set_user_db_path(p)

        with contextlib.ExitStack() as stack:
            copy = stack.enter_context(unittest.mock.patch(
                "copy.copy"
            ))

            run_in_executor = stack.enter_context(unittest.mock.patch.object(
                asyncio.get_event_loop(),
                "run_in_executor"
            ))

            async_ = stack.enter_context(unittest.mock.patch(
                "asyncio.ensure_future"
            ))

            self.c.add_cache_entry(
                key,
                q,
            )

        copy.assert_called_once_with(q)

        p.__truediv__.assert_called_once_with(key.path)

        run_in_executor.assert_called_with(
            None,
            entitycaps_service.writeback,
            p.__truediv__(),
            q.captured_events,
        )
        async_.assert_called_with(run_in_executor())

        result = self.c.lookup_in_database(key)
        self.assertEqual(result, copy())

    def test_add_cache_entry_does_not_perform_writeback_if_no_userdb_is_set(self):  # NOQA
        q = disco.xso.InfoQuery()

        with contextlib.ExitStack() as stack:
            copy = stack.enter_context(unittest.mock.patch(
                "copy.copy"
            ))

            run_in_executor = stack.enter_context(unittest.mock.patch.object(
                asyncio.get_event_loop(),
                "run_in_executor"
            ))

            async_ = stack.enter_context(unittest.mock.patch(
                "asyncio.ensure_future"
            ))

            self.c.add_cache_entry(
                unittest.mock.sentinel.key,
                q,
            )

        copy.assert_called_with(q)
        self.assertFalse(run_in_executor.mock_calls)
        self.assertFalse(async_.mock_calls)

        result = self.c.lookup_in_database(unittest.mock.sentinel.key)
        self.assertEqual(result, copy())

    def test_writeback_from_add_cache_entry_creates_file(self):
        q = disco.xso.InfoQuery()
        q.captured_events = [
            ("start", q.TAG[0], q.TAG[1], {}),
            ("end",)
        ]
        key = unittest.mock.Mock()

        with contextlib.ExitStack() as stack:
            tempdir = stack.enter_context(
                tempfile.TemporaryDirectory()
            )

            p = pathlib.Path(tempdir)
            key.path = pathlib.Path("key") / "path" / "used"

            self.c.set_user_db_path(p)

            copy = stack.enter_context(unittest.mock.patch(
                "copy.copy"
            ))

            run_in_executor = stack.enter_context(unittest.mock.patch.object(
                asyncio.get_event_loop(),
                "run_in_executor"
            ))

            async_ = stack.enter_context(unittest.mock.patch(
                "asyncio.ensure_future"
            ))

            self.c.add_cache_entry(
                key,
                q,
            )

            copy.assert_called_once_with(q)

            run_in_executor.assert_called_with(
                None,
                entitycaps_service.writeback,
                p / key.path,
                q.captured_events,
            )
            async_.assert_called_with(run_in_executor())

            entitycaps_service.writeback(
                *run_in_executor.mock_calls[0][1][2:]
            )

            self.assertTrue((p / key.path).is_file())


class TestService(unittest.TestCase):
    def setUp(self):
        self.cc = make_connected_client()
        self.disco_client = unittest.mock.Mock()
        self.disco_client.query_info = CoroutineMock()
        self.disco_client.query_info.side_effect = AssertionError()
        self.disco_server = unittest.mock.Mock()
        self.disco_server.on_info_changed.context_connect = \
            unittest.mock.MagicMock()
        self.disco_server.iter_items.return_value = []

        self.impl115 = unittest.mock.Mock()
        self.impl115.extract_keys.return_value = []
        self.impl115.calculate_keys.return_value = []

        self.impl390 = unittest.mock.Mock()
        self.impl390.extract_keys.return_value = []
        self.impl390.calculate_keys.return_value = []

        with contextlib.ExitStack() as stack:
            Implementation115 = stack.enter_context(
                unittest.mock.patch(
                    "aioxmpp.entitycaps.caps115.Implementation"
                )
            )
            Implementation115.return_value = self.impl115

            Implementation390 = stack.enter_context(
                unittest.mock.patch(
                    "aioxmpp.entitycaps.caps390.Implementation"
                )
            )
            Implementation390.return_value = self.impl390

            self.s = entitycaps_service.EntityCapsService(
                self.cc,
                dependencies={
                    disco.DiscoClient: self.disco_client,
                    disco.DiscoServer: self.disco_server,
                }
            )

        Implementation115.assert_called_once_with(
            entitycaps_service.EntityCapsService.NODE
        )

        Implementation390.assert_called_once_with(
            aioxmpp.hashes.default_hash_algorithms
        )

        self.disco_client.mock_calls.clear()
        self.disco_server.mock_calls.clear()
        self.cc.mock_calls.clear()

        self.disco_server.iter_features.return_value = [
            "http://jabber.org/protocol/disco#items",
            "http://jabber.org/protocol/disco#info",
        ]

        self.disco_server.iter_identities.return_value = [
            ("client", "pc", None, None),
            ("client", "pc", structs.LanguageTag.fromstr("en"), "foo"),
        ]

    def test_is_Service_subclass(self):
        self.assertTrue(issubclass(
            entitycaps_service.EntityCapsService,
            service.Service
        ))

    def test_registers_xep115_feature(self):
        self.assertIsInstance(
            entitycaps_service.EntityCapsService._xep115_feature,
            aioxmpp.disco.register_feature,
        )
        self.assertEqual(
            entitycaps_service.EntityCapsService._xep115_feature.feature,
            namespaces.xep0115_caps,
        )

    def test_registers_xep390_feature(self):
        self.assertIsInstance(
            entitycaps_service.EntityCapsService._xep390_feature,
            aioxmpp.disco.register_feature,
        )
        self.assertEqual(
            entitycaps_service.EntityCapsService._xep390_feature.feature,
            namespaces.xep0390_caps,
        )

    def test_xep115_support_sets_xep115_feature_enabledness(self):
        self.assertTrue(self.s.xep115_support)
        self.assertTrue(self.s._xep115_feature.enabled)

        self.s.xep115_support = False

        self.assertFalse(self.s.xep115_support)
        self.assertFalse(self.s._xep115_feature.enabled)

        self.s.xep115_support = True

        self.assertTrue(self.s.xep115_support)
        self.assertTrue(self.s._xep115_feature.enabled)

    def test_xep390_support_sets_xep390_feature_enabledness(self):
        self.assertTrue(self.s.xep390_support)
        self.assertTrue(self.s._xep390_feature.enabled)

        self.s.xep390_support = False

        self.assertFalse(self.s.xep390_support)
        self.assertFalse(self.s._xep390_feature.enabled)

        self.s.xep390_support = True

        self.assertTrue(self.s.xep390_support)
        self.assertTrue(self.s._xep390_feature.enabled)

    def test_after_disco(self):
        self.assertIn(
            disco.DiscoServer,
            entitycaps_service.EntityCapsService.ORDER_AFTER
        )
        self.assertIn(
            disco.DiscoClient,
            entitycaps_service.EntityCapsService.ORDER_AFTER
        )

    def test_handle_outbound_presence_is_decorated(self):
        self.assertTrue(
            service.is_outbound_presence_filter(
                entitycaps_service.EntityCapsService.handle_outbound_presence,
            )
        )

    def test_handle_inbound_presence_is_decorated(self):
        self.assertTrue(
            service.is_inbound_presence_filter(
                entitycaps_service.EntityCapsService.handle_inbound_presence,
            )
        )

    def test_cache_defaults(self):
        self.assertIsInstance(
            self.s.cache,
            entitycaps_service.Cache
        )

    def test_cache_defaults_when_deleted(self):
        c1 = self.s.cache
        del self.s.cache
        c2 = self.s.cache
        self.assertIsNot(c1, c2)
        self.assertIsInstance(c2, entitycaps_service.Cache)

    def test_cache_can_be_set(self):
        c = unittest.mock.Mock()
        self.s.cache = c
        self.assertIs(self.s.cache, c)

    def test_handle_inbound_presence_extracts_115_keys_and_spawns_lookup(self):
        presence = unittest.mock.Mock(spec=aioxmpp.Presence)

        self.impl115.extract_keys.return_value = iter([
            unittest.mock.sentinel.key1,
        ])

        with contextlib.ExitStack() as stack:
            LazyTask = stack.enter_context(
                unittest.mock.patch("aioxmpp.utils.LazyTask")
            )

            lookup_info = stack.enter_context(
                unittest.mock.patch.object(self.s, "lookup_info")
            )

            result = self.s.handle_inbound_presence(presence)

        self.impl115.extract_keys.assert_called_once_with(presence)

        LazyTask.assert_called_once_with(
            lookup_info,
            presence.from_,
            [
                unittest.mock.sentinel.key1,
            ]
        )

        self.disco_client.set_info_future.assert_called_with(
            presence.from_,
            None,
            LazyTask(),
        )

        self.assertEqual(result, presence)

    def test_handle_inbound_presence_extracts_390_keys_and_spawns_lookup(self):
        presence = unittest.mock.Mock(spec=aioxmpp.Presence)

        self.impl390.extract_keys.return_value = iter([
            unittest.mock.sentinel.key1,
        ])

        with contextlib.ExitStack() as stack:
            LazyTask = stack.enter_context(
                unittest.mock.patch("aioxmpp.utils.LazyTask")
            )

            lookup_info = stack.enter_context(
                unittest.mock.patch.object(self.s, "lookup_info")
            )

            result = self.s.handle_inbound_presence(presence)

        self.impl390.extract_keys.assert_called_once_with(presence)

        LazyTask.assert_called_once_with(
            lookup_info,
            presence.from_,
            [
                unittest.mock.sentinel.key1,
            ]
        )

        self.disco_client.set_info_future.assert_called_with(
            presence.from_,
            None,
            LazyTask(),
        )

        self.assertEqual(result, presence)

    def test_handle_inbound_presence_extracts_both_keys_and_spawns_lookup(self):  # NOQA
        presence = unittest.mock.Mock(spec=aioxmpp.Presence)

        self.impl115.extract_keys.return_value = iter([
            unittest.mock.sentinel.key1,
        ])

        self.impl390.extract_keys.return_value = iter([
            unittest.mock.sentinel.key2,
            unittest.mock.sentinel.key3,
        ])

        with contextlib.ExitStack() as stack:
            LazyTask = stack.enter_context(
                unittest.mock.patch("aioxmpp.utils.LazyTask")
            )

            lookup_info = stack.enter_context(
                unittest.mock.patch.object(self.s, "lookup_info")
            )

            result = self.s.handle_inbound_presence(presence)

        self.impl390.extract_keys.assert_called_once_with(presence)

        LazyTask.assert_called_once_with(
            lookup_info,
            presence.from_,
            [
                unittest.mock.sentinel.key2,
                unittest.mock.sentinel.key3,
                unittest.mock.sentinel.key1,
            ]
        )

        self.disco_client.set_info_future.assert_called_with(
            presence.from_,
            None,
            LazyTask(),
        )

        self.assertEqual(result, presence)

    def test_handle_inbound_presence_ignores_115_if_disabled(self):
        self.s.xep115_support = False

        presence = unittest.mock.Mock(spec=aioxmpp.Presence)

        self.impl115.extract_keys.return_value = iter([
            unittest.mock.sentinel.key1,
        ])

        self.impl390.extract_keys.return_value = iter([
            unittest.mock.sentinel.key2,
            unittest.mock.sentinel.key3,
        ])

        with contextlib.ExitStack() as stack:
            LazyTask = stack.enter_context(
                unittest.mock.patch("aioxmpp.utils.LazyTask")
            )

            lookup_info = stack.enter_context(
                unittest.mock.patch.object(self.s, "lookup_info")
            )

            result = self.s.handle_inbound_presence(presence)

        self.impl115.extract_keys.assert_not_called()
        self.impl390.extract_keys.assert_called_once_with(presence)

        LazyTask.assert_called_once_with(
            lookup_info,
            presence.from_,
            [
                unittest.mock.sentinel.key2,
                unittest.mock.sentinel.key3,
            ]
        )

        self.disco_client.set_info_future.assert_called_with(
            presence.from_,
            None,
            LazyTask(),
        )

        self.assertEqual(result, presence)

    def test_handle_inbound_presence_ignores_390_if_disabled(self):
        self.s.xep390_support = False

        presence = unittest.mock.Mock(spec=aioxmpp.Presence)

        self.impl115.extract_keys.return_value = iter([
            unittest.mock.sentinel.key1,
        ])

        self.impl390.extract_keys.return_value = iter([
            unittest.mock.sentinel.key2,
            unittest.mock.sentinel.key3,
        ])

        with contextlib.ExitStack() as stack:
            LazyTask = stack.enter_context(
                unittest.mock.patch("aioxmpp.utils.LazyTask")
            )

            lookup_info = stack.enter_context(
                unittest.mock.patch.object(self.s, "lookup_info")
            )

            result = self.s.handle_inbound_presence(presence)

        self.impl115.extract_keys.assert_called_once_with(presence)
        self.impl390.extract_keys.assert_not_called()

        LazyTask.assert_called_once_with(
            lookup_info,
            presence.from_,
            [
                unittest.mock.sentinel.key1,
            ]
        )

        self.disco_client.set_info_future.assert_called_with(
            presence.from_,
            None,
            LazyTask(),
        )

        self.assertEqual(result, presence)

    def test_query_and_cache(self):
        self.maxDiff = None

        ver = TEST_DB_ENTRY_VER
        response = TEST_DB_ENTRY

        base = unittest.mock.Mock()
        base.disco = self.disco_client
        base.disco.query_info.side_effect = None
        base.key.verify.return_value = True
        with contextlib.ExitStack() as stack:
            stack.enter_context(unittest.mock.patch.object(
                self.s.cache,
                "add_cache_entry",
                new=base.add_cache_entry
            ))

            base.disco.query_info.return_value = response

            result = run_coroutine(self.s.query_and_cache(
                TEST_FROM,
                base.key,
                base.fut,
            ))

        calls = list(base.mock_calls)
        self.assertSequenceEqual(
            calls,
            [
                unittest.mock.call.disco.query_info(
                    TEST_FROM,
                    node=base.key.node,
                    require_fresh=True,
                    no_cache=True,
                ),
                unittest.mock.call.key.verify(response),
                unittest.mock.call.add_cache_entry(
                    base.key,
                    response,
                ),
                unittest.mock.call.fut.set_result(
                    result,
                )
            ]
        )

        self.assertEqual(result, response)

    def test_query_and_cache_checks_hash(self):
        self.maxDiff = None

        ver = TEST_DB_ENTRY_VER
        response = TEST_DB_ENTRY

        base = unittest.mock.Mock()
        base.disco = self.disco_client
        base.disco.query_info.side_effect = None
        base.key.verify.return_value = False
        with contextlib.ExitStack() as stack:
            stack.enter_context(unittest.mock.patch.object(
                self.s.cache,
                "add_cache_entry",
                new=base.add_cache_entry
            ))

            base.disco.query_info.return_value = response

            result = run_coroutine(self.s.query_and_cache(
                TEST_FROM,
                base.key,
                base.fut,
            ))

        calls = list(base.mock_calls)
        self.assertSequenceEqual(
            calls,
            [
                unittest.mock.call.disco.query_info(
                    TEST_FROM,
                    node=base.key.node,
                    require_fresh=True,
                    no_cache=True,
                ),
                unittest.mock.call.key.verify(response),
                unittest.mock.call.fut.set_exception(unittest.mock.ANY)
            ]
        )

        _, (exc,), _ = base.fut.mock_calls[0]
        self.assertIsInstance(exc, ValueError)

        self.assertEqual(result, response)

    def test_query_and_cache_does_not_cache_on_ValueError(self):
        self.maxDiff = None

        response = TEST_DB_ENTRY
        exc = ValueError()

        base = unittest.mock.Mock()
        base.disco = self.disco_client
        base.disco.query_info.side_effect = None
        base.key.verify.side_effect = exc
        with contextlib.ExitStack() as stack:
            stack.enter_context(unittest.mock.patch.object(
                self.s.cache,
                "add_cache_entry",
                new=base.add_cache_entry
            ))

            base.disco.query_info.return_value = response

            result = run_coroutine(self.s.query_and_cache(
                TEST_FROM,
                base.key,
                base.fut,
            ))

        calls = list(base.mock_calls)
        self.assertSequenceEqual(
            calls,
            [
                unittest.mock.call.disco.query_info(
                    TEST_FROM,
                    node=base.key.node,
                    require_fresh=True,
                    no_cache=True,
                ),
                unittest.mock.call.key.verify(response),
                unittest.mock.call.fut.set_exception(exc)
            ]
        )

        self.assertEqual(result, response)

    def test_lookup_info_asks_cache_first_and_returns_value(self):
        base = unittest.mock.Mock()
        base.disco = self.disco_client
        base.disco.query_info.side_effect = None
        base.query_and_cache = CoroutineMock()
        base.lookup = CoroutineMock()

        with contextlib.ExitStack() as stack:
            stack.enter_context(unittest.mock.patch.object(
                self.s.cache,
                "lookup",
                new=base.lookup,
            ))

            stack.enter_context(unittest.mock.patch.object(
                self.s,
                "query_and_cache",
                new=base.query_and_cache
            ))

            base.lookup.return_value = unittest.mock.sentinel.cache_result

            result = run_coroutine(self.s.lookup_info(
                TEST_FROM,
                [
                    unittest.mock.sentinel.key,
                ]
            ))

        self.assertSequenceEqual(
            base.mock_calls,
            [
                unittest.mock.call.lookup(unittest.mock.sentinel.key),
            ]
        )

        self.assertIs(result, unittest.mock.sentinel.cache_result)

    def test_lookup_info_asks_cache_for_all_keys_and_returns_value(self):
        base = unittest.mock.Mock()
        base.disco = self.disco_client
        base.disco.query_info.side_effect = None
        base.query_and_cache = CoroutineMock()
        base.lookup = CoroutineMock()

        ncall = 0

        def lookup_side_effect(*args, **kwargs):
            nonlocal ncall
            ncall += 1
            if ncall == 2:
                return unittest.mock.sentinel.cache_result
            raise KeyError()

        with contextlib.ExitStack() as stack:
            stack.enter_context(unittest.mock.patch.object(
                self.s.cache,
                "lookup",
                new=base.lookup,
            ))

            stack.enter_context(unittest.mock.patch.object(
                self.s,
                "query_and_cache",
                new=base.query_and_cache
            ))

            base.lookup.side_effect = lookup_side_effect

            result = run_coroutine(self.s.lookup_info(
                TEST_FROM,
                [
                    unittest.mock.sentinel.key1,
                    unittest.mock.sentinel.key2,
                ]
            ))

        self.assertSequenceEqual(
            base.mock_calls,
            [
                unittest.mock.call.lookup(unittest.mock.sentinel.key1),
                unittest.mock.call.lookup(unittest.mock.sentinel.key2),
            ]
        )

        self.assertIs(result, unittest.mock.sentinel.cache_result)

    def test_lookup_info_delegates_to_query_and_cache_on_miss(self):
        base = unittest.mock.Mock()
        base.disco = self.disco_client
        base.disco.query_info.side_effect = None
        base.query_and_cache = CoroutineMock()

        with contextlib.ExitStack() as stack:
            stack.enter_context(unittest.mock.patch.object(
                self.s.cache,
                "lookup",
                new=base.lookup
            ))

            stack.enter_context(unittest.mock.patch.object(
                self.s.cache,
                "create_query_future",
                new=base.create_query_future
            ))

            stack.enter_context(unittest.mock.patch.object(
                self.s,
                "query_and_cache",
                new=base.query_and_cache
            ))

            base.lookup.side_effect = KeyError()
            base.query_and_cache.return_value = \
                unittest.mock.sentinel.query_result

            result = run_coroutine(self.s.lookup_info(
                TEST_FROM,
                [
                    unittest.mock.sentinel.key1,
                    unittest.mock.sentinel.key2,
                ]
            ))

        calls = list(base.mock_calls)
        self.assertSequenceEqual(
            calls,
            [
                unittest.mock.call.lookup(unittest.mock.sentinel.key1),
                unittest.mock.call.lookup(unittest.mock.sentinel.key2),
                unittest.mock.call.create_query_future(
                    unittest.mock.sentinel.key1,
                ),
                unittest.mock.call.query_and_cache(
                    TEST_FROM,
                    unittest.mock.sentinel.key1,
                    base.create_query_future()
                )
            ]
        )

        self.assertIs(result, unittest.mock.sentinel.query_result)

    def test_update_hash(self):
        base = unittest.mock.Mock()

        self.impl115.calculate_keys.return_value = iter([
            base.key1,
        ])

        self.impl390.calculate_keys.return_value = iter([
            base.key2,
            base.key3,
        ])

        with contextlib.ExitStack() as stack:
            hash_query = stack.enter_context(
                unittest.mock.patch(
                    "aioxmpp.entitycaps.caps115.hash_query"
                )
            )

            clone = stack.enter_context(
                unittest.mock.patch.object(
                    disco.StaticNode,
                    "clone",
                )
            )

            push_hashset = stack.enter_context(
                unittest.mock.patch.object(
                    self.s,
                    "_push_hashset",
                )
            )
            push_hashset.return_value = True

            with self.s.on_ver_changed.context_connect(base.cb):
                self.s.update_hash()

        hash_query.assert_not_called()

        clone.assert_called_once_with(self.disco_server)
        clone().as_info_xso.assert_called_once_with()

        self.impl115.calculate_keys.assert_called_once_with(
            clone().as_info_xso()
        )

        self.impl390.calculate_keys.assert_called_once_with(
            clone().as_info_xso()
        )

        self.disco_server.mount_node.assert_not_called()

        push_hashset.assert_called_once_with(
            clone(),
            {
                self.impl115: {base.key1},
                self.impl390: {base.key2, base.key3},
            }
        )

        base.cb.assert_called_once_with()

    def test_update_hash_does_not_emit_on_ver_changed_if_push_hashset_returns_false(self):  # NOQA
        base = unittest.mock.Mock()

        self.impl115.calculate_keys.return_value = iter([
            base.key1,
        ])

        self.impl390.calculate_keys.return_value = iter([
            base.key2,
            base.key3,
        ])

        with contextlib.ExitStack() as stack:
            hash_query = stack.enter_context(
                unittest.mock.patch(
                    "aioxmpp.entitycaps.caps115.hash_query"
                )
            )

            clone = stack.enter_context(
                unittest.mock.patch.object(
                    disco.StaticNode,
                    "clone",
                )
            )

            push_hashset = stack.enter_context(
                unittest.mock.patch.object(
                    self.s,
                    "_push_hashset",
                )
            )
            push_hashset.return_value = False

            with self.s.on_ver_changed.context_connect(base.cb):
                self.s.update_hash()

        hash_query.assert_not_called()

        clone.assert_called_once_with(self.disco_server)
        clone().as_info_xso.assert_called_once_with()

        self.impl115.calculate_keys.assert_called_once_with(
            clone().as_info_xso()
        )

        self.impl390.calculate_keys.assert_called_once_with(
            clone().as_info_xso()
        )

        self.disco_server.mount_node.assert_not_called()

        push_hashset.assert_called_once_with(
            clone(),
            {
                self.impl115: {base.key1},
                self.impl390: {base.key2, base.key3},
            }
        )

        base.cb.assert_not_called()

    def test_update_hash_ignores_115_if_disabled(self):
        self.s.xep115_support = False
        self.disco_server.reset_mock()

        base = unittest.mock.Mock()

        self.impl115.calculate_keys.return_value = iter([
            base.key1,
        ])

        self.impl390.calculate_keys.return_value = iter([
            base.key2,
            base.key3,
        ])

        with contextlib.ExitStack() as stack:
            hash_query = stack.enter_context(
                unittest.mock.patch(
                    "aioxmpp.entitycaps.caps115.hash_query"
                )
            )

            clone = stack.enter_context(
                unittest.mock.patch.object(
                    disco.StaticNode,
                    "clone",
                )
            )

            push_hashset = stack.enter_context(
                unittest.mock.patch.object(
                    self.s,
                    "_push_hashset",
                )
            )

            self.s.update_hash()

        hash_query.assert_not_called()

        clone.assert_called_once_with(self.disco_server)
        clone().as_info_xso.assert_called_once_with()

        self.impl115.calculate_keys.assert_not_called()

        self.impl390.calculate_keys.assert_called_once_with(
            clone().as_info_xso()
        )

        self.disco_server.mount_node.assert_not_called()

        push_hashset.assert_called_once_with(
            clone(),
            {
                self.impl390: {base.key2, base.key3},
            }
        )

    def test_update_hash_ignores_390_if_disabled(self):
        self.s.xep390_support = False
        self.disco_server.reset_mock()

        base = unittest.mock.Mock()

        self.impl115.calculate_keys.return_value = iter([
            base.key1,
        ])

        self.impl390.calculate_keys.return_value = iter([
            base.key2,
            base.key3,
        ])

        with contextlib.ExitStack() as stack:
            hash_query = stack.enter_context(
                unittest.mock.patch(
                    "aioxmpp.entitycaps.caps115.hash_query"
                )
            )

            clone = stack.enter_context(
                unittest.mock.patch.object(
                    disco.StaticNode,
                    "clone",
                )
            )

            push_hashset = stack.enter_context(
                unittest.mock.patch.object(
                    self.s,
                    "_push_hashset",
                )
            )

            self.s.update_hash()

        hash_query.assert_not_called()

        clone.assert_called_once_with(self.disco_server)
        clone().as_info_xso.assert_called_once_with()

        self.impl115.calculate_keys.assert_called_once_with(
            clone().as_info_xso()
        )

        self.impl390.calculate_keys.assert_not_called()

        self.disco_server.mount_node.assert_not_called()

        push_hashset.assert_called_once_with(
            clone(),
            {
                self.impl115: {base.key1},
            }
        )

    def test__push_hashset_registers_nodes(self):
        base = unittest.mock.Mock()

        self.s._push_hashset(
            unittest.mock.sentinel.node,
            {
                unittest.mock.sentinel.impl1: {
                    base.key1,
                },
                unittest.mock.sentinel.impl2: {
                    base.key2,
                    base.key3,
                }
            }
        )

        self.assertCountEqual(
            self.disco_server.mount_node.mock_calls,
            [
                unittest.mock.call(base.key1.node,
                                   unittest.mock.sentinel.node),
                unittest.mock.call(base.key2.node,
                                   unittest.mock.sentinel.node),
                unittest.mock.call(base.key3.node,
                                   unittest.mock.sentinel.node),
            ]
        )

    def test__push_hashset_keeps_three_hashsets(self):
        base = unittest.mock.Mock()

        self.s._push_hashset(
            unittest.mock.sentinel.node1,
            {
                unittest.mock.sentinel.impl1: {
                    base.key1,
                },
                unittest.mock.sentinel.impl2: {
                    base.key2,
                    base.key3,
                }
            }
        )

        self.s._push_hashset(
            unittest.mock.sentinel.node2,
            {
                unittest.mock.sentinel.impl1: {
                    base.key4,
                },
                unittest.mock.sentinel.impl2: {
                    base.key5,
                }
            }
        )

        self.s._push_hashset(
            unittest.mock.sentinel.node3,
            {
                unittest.mock.sentinel.impl1: {
                    base.key6,
                },
                unittest.mock.sentinel.impl2: {
                    base.key7,
                }
            }
        )

        self.assertCountEqual(
            self.disco_server.mount_node.mock_calls,
            [
                unittest.mock.call(base.key1.node,
                                   unittest.mock.sentinel.node1),
                unittest.mock.call(base.key2.node,
                                   unittest.mock.sentinel.node1),
                unittest.mock.call(base.key3.node,
                                   unittest.mock.sentinel.node1),
                unittest.mock.call(base.key4.node,
                                   unittest.mock.sentinel.node2),
                unittest.mock.call(base.key5.node,
                                   unittest.mock.sentinel.node2),
                unittest.mock.call(base.key6.node,
                                   unittest.mock.sentinel.node3),
                unittest.mock.call(base.key7.node,
                                   unittest.mock.sentinel.node3),
            ]
        )

        self.assertCountEqual(
            self.disco_server.unmount_node.mock_calls,
            [],
        )

    def test__push_hashset_fifo_behaviour(self):
        base = unittest.mock.Mock()

        self.s._push_hashset(
            unittest.mock.sentinel.node1,
            {
                unittest.mock.sentinel.impl1: {
                    base.key1,
                },
                unittest.mock.sentinel.impl2: {
                    base.key2,
                    base.key3,
                }
            }
        )

        self.s._push_hashset(
            unittest.mock.sentinel.node2,
            {
                unittest.mock.sentinel.impl1: {
                    base.key4,
                },
                unittest.mock.sentinel.impl2: {
                    base.key5,
                }
            }
        )

        self.s._push_hashset(
            unittest.mock.sentinel.node3,
            {
                unittest.mock.sentinel.impl1: {
                    base.key6,
                },
                unittest.mock.sentinel.impl2: {
                    base.key7,
                }
            }
        )

        self.s._push_hashset(
            unittest.mock.sentinel.node4,
            {
                unittest.mock.sentinel.impl1: {
                    base.key8,
                },
                unittest.mock.sentinel.impl2: {
                    base.key9,
                    base.key10,
                }
            }
        )

        self.assertCountEqual(
            self.disco_server.mount_node.mock_calls,
            [
                unittest.mock.call(base.key1.node,
                                   unittest.mock.sentinel.node1),
                unittest.mock.call(base.key2.node,
                                   unittest.mock.sentinel.node1),
                unittest.mock.call(base.key3.node,
                                   unittest.mock.sentinel.node1),
                unittest.mock.call(base.key4.node,
                                   unittest.mock.sentinel.node2),
                unittest.mock.call(base.key5.node,
                                   unittest.mock.sentinel.node2),
                unittest.mock.call(base.key6.node,
                                   unittest.mock.sentinel.node3),
                unittest.mock.call(base.key7.node,
                                   unittest.mock.sentinel.node3),
                unittest.mock.call(base.key8.node,
                                   unittest.mock.sentinel.node4),
                unittest.mock.call(base.key9.node,
                                   unittest.mock.sentinel.node4),
                unittest.mock.call(base.key10.node,
                                   unittest.mock.sentinel.node4),
            ]
        )

        self.assertCountEqual(
            self.disco_server.unmount_node.mock_calls,
            [
                unittest.mock.call(base.key1.node),
                unittest.mock.call(base.key2.node),
                unittest.mock.call(base.key3.node),
            ],
        )

        self.disco_server.unmount_node.reset_mock()
        self.disco_server.mount_node.reset_mock()

        self.s._push_hashset(
            unittest.mock.sentinel.node5,
            {
                unittest.mock.sentinel.impl1: {
                    base.key11,
                },
                unittest.mock.sentinel.impl2: {
                    base.key12,
                    base.key13,
                }
            }
        )

        self.assertCountEqual(
            self.disco_server.mount_node.mock_calls,
            [
                unittest.mock.call(base.key11.node,
                                   unittest.mock.sentinel.node5),
                unittest.mock.call(base.key12.node,
                                   unittest.mock.sentinel.node5),
                unittest.mock.call(base.key13.node,
                                   unittest.mock.sentinel.node5),
            ]
        )

        self.assertCountEqual(
            self.disco_server.unmount_node.mock_calls,
            [
                unittest.mock.call(base.key4.node),
                unittest.mock.call(base.key5.node),
            ],
        )

    def test__push_hashset_can_deal_with_hash_collisions(self):
        # I know we’re insane to even consider this…
        base = unittest.mock.Mock()

        self.s._push_hashset(
            unittest.mock.sentinel.node1,
            {
                unittest.mock.sentinel.impl1: {
                    base.key1,
                },
                unittest.mock.sentinel.impl2: {
                    base.key2,
                    base.key3,
                }
            }
        )

        self.s._push_hashset(
            unittest.mock.sentinel.node2,
            {
                unittest.mock.sentinel.impl1: {
                    base.key1,
                },
                unittest.mock.sentinel.impl2: {
                    base.key5,
                }
            }
        )

        self.s._push_hashset(
            unittest.mock.sentinel.node3,
            {
                unittest.mock.sentinel.impl1: {
                    base.key6,
                },
                unittest.mock.sentinel.impl2: {
                    base.key7,
                }
            }
        )

        self.s._push_hashset(
            unittest.mock.sentinel.node4,
            {
                unittest.mock.sentinel.impl1: {
                    base.key8,
                },
                unittest.mock.sentinel.impl2: {
                    base.key9,
                    base.key10,
                }
            }
        )

        self.assertCountEqual(
            self.disco_server.mount_node.mock_calls,
            [
                unittest.mock.call(base.key1.node,
                                   unittest.mock.sentinel.node1),
                unittest.mock.call(base.key2.node,
                                   unittest.mock.sentinel.node1),
                unittest.mock.call(base.key3.node,
                                   unittest.mock.sentinel.node1),
                unittest.mock.call(base.key5.node,
                                   unittest.mock.sentinel.node2),
                unittest.mock.call(base.key6.node,
                                   unittest.mock.sentinel.node3),
                unittest.mock.call(base.key7.node,
                                   unittest.mock.sentinel.node3),
                unittest.mock.call(base.key8.node,
                                   unittest.mock.sentinel.node4),
                unittest.mock.call(base.key9.node,
                                   unittest.mock.sentinel.node4),
                unittest.mock.call(base.key10.node,
                                   unittest.mock.sentinel.node4),
            ]
        )

        self.assertCountEqual(
            self.disco_server.unmount_node.mock_calls,
            [
                unittest.mock.call(base.key2.node),
                unittest.mock.call(base.key3.node),
            ],
        )

        self.disco_server.unmount_node.reset_mock()
        self.disco_server.mount_node.reset_mock()

        self.s._push_hashset(
            unittest.mock.sentinel.node5,
            {
                unittest.mock.sentinel.impl1: {
                    base.key11,
                },
                unittest.mock.sentinel.impl2: {
                    base.key12,
                    base.key13,
                }
            }
        )

        self.assertCountEqual(
            self.disco_server.mount_node.mock_calls,
            [
                unittest.mock.call(base.key11.node,
                                   unittest.mock.sentinel.node5),
                unittest.mock.call(base.key12.node,
                                   unittest.mock.sentinel.node5),
                unittest.mock.call(base.key13.node,
                                   unittest.mock.sentinel.node5),
            ]
        )

        self.assertCountEqual(
            self.disco_server.unmount_node.mock_calls,
            [
                unittest.mock.call(base.key1.node),
                unittest.mock.call(base.key5.node),
            ],
        )

    def test__push_hashset_noop_and_returs_false_on_dup(self):
        base = unittest.mock.Mock()

        self.assertTrue(self.s._push_hashset(
            unittest.mock.sentinel.node1,
            {
                unittest.mock.sentinel.impl1: {
                    base.key1,
                },
                unittest.mock.sentinel.impl2: {
                    base.key2,
                    base.key3,
                }
            }
        ))

        self.assertTrue(self.s._push_hashset(
            unittest.mock.sentinel.node2,
            {
                unittest.mock.sentinel.impl1: {
                    base.key4,
                },
                unittest.mock.sentinel.impl2: {
                    base.key5,
                }
            }
        ))

        self.assertTrue(self.s._push_hashset(
            unittest.mock.sentinel.node3,
            {
                unittest.mock.sentinel.impl1: {
                    base.key6,
                },
                unittest.mock.sentinel.impl2: {
                    base.key7,
                }
            }
        ))

        self.assertTrue(self.s._push_hashset(
            unittest.mock.sentinel.node4,
            {
                unittest.mock.sentinel.impl1: {
                    base.key8,
                },
                unittest.mock.sentinel.impl2: {
                    base.key9,
                    base.key10,
                }
            }
        ))

        self.assertFalse(self.s._push_hashset(
            unittest.mock.sentinel.node5,
            {
                unittest.mock.sentinel.impl1: {
                    base.key8,
                },
                unittest.mock.sentinel.impl2: {
                    base.key9,
                    base.key10,
                }
            }
        ))

        self.assertCountEqual(
            self.disco_server.mount_node.mock_calls,
            [
                unittest.mock.call(base.key1.node,
                                   unittest.mock.sentinel.node1),
                unittest.mock.call(base.key2.node,
                                   unittest.mock.sentinel.node1),
                unittest.mock.call(base.key3.node,
                                   unittest.mock.sentinel.node1),
                unittest.mock.call(base.key4.node,
                                   unittest.mock.sentinel.node2),
                unittest.mock.call(base.key5.node,
                                   unittest.mock.sentinel.node2),
                unittest.mock.call(base.key6.node,
                                   unittest.mock.sentinel.node3),
                unittest.mock.call(base.key7.node,
                                   unittest.mock.sentinel.node3),
                unittest.mock.call(base.key8.node,
                                   unittest.mock.sentinel.node4),
                unittest.mock.call(base.key9.node,
                                   unittest.mock.sentinel.node4),
                unittest.mock.call(base.key10.node,
                                   unittest.mock.sentinel.node4),
            ]
        )

        self.assertCountEqual(
            self.disco_server.unmount_node.mock_calls,
            [
                unittest.mock.call(base.key1.node),
                unittest.mock.call(base.key2.node),
                unittest.mock.call(base.key3.node),
            ],
        )

    def test__info_changed_calls_update_hash_soon(self):
        with contextlib.ExitStack() as stack:
            get_event_loop = stack.enter_context(unittest.mock.patch(
                "asyncio.get_event_loop"
            ))

            self.s._info_changed()

        get_event_loop.assert_called_with()
        get_event_loop().call_soon.assert_called_with(
            self.s.update_hash
        )

    def test_handle_outbound_presence_inserts_keys(self):
        base = unittest.mock.Mock()
        self.impl115.calculate_keys.return_value = iter([
            base.key1,
        ])
        self.impl390.calculate_keys.return_value = iter([
            base.key2,
            base.key3,
        ])

        self.s._push_hashset(
            unittest.mock.sentinel.node,
            {
                self.impl115: {base.key1},
                self.impl390: {base.key2, base.key3},
            }
        )

        presence = stanza.Presence()
        result = self.s.handle_outbound_presence(presence)
        self.assertIs(result, presence)

        self.impl115.put_keys.assert_called_once_with(
            {base.key1},
            presence,
        )

        self.impl390.put_keys.assert_called_once_with(
            {base.key2, base.key3},
            presence,
        )

    def test_handle_outbound_presence_does_not_attach_caps_to_non_available(
            self):
        base = unittest.mock.Mock()
        self.impl115.calculate_keys.return_value = iter([
            base.key1,
        ])
        self.impl390.calculate_keys.return_value = iter([
            base.key2,
            base.key3,
        ])

        self.s._push_hashset(
            unittest.mock.sentinel.node,
            {
                self.impl115: {base.key1},
                self.impl390: {base.key2, base.key3},
            }
        )

        types = [
            structs.PresenceType.UNAVAILABLE,
            structs.PresenceType.SUBSCRIBE,
            structs.PresenceType.SUBSCRIBED,
            structs.PresenceType.UNSUBSCRIBE,
            structs.PresenceType.UNSUBSCRIBED,
            structs.PresenceType.ERROR,
        ]

        for type_ in types:
            presence = stanza.Presence(type_=type_)
            self.s.handle_outbound_presence(presence)

        self.impl115.put_keys.assert_not_called()

    def test_handle_outbound_presence_does_not_call_put_keys_if_unset(self):
        presence = stanza.Presence()
        self.s.handle_outbound_presence(presence)
        self.impl115.put_keys.assert_not_called()


class Testwriteback(unittest.TestCase):
    def test_uses_tempfile_atomically_and_serialises_xso(self):
        base = unittest.mock.Mock()
        base.p = unittest.mock.MagicMock()
        base.NamedTemporaryFile = unittest.mock.MagicMock()

        with contextlib.ExitStack() as stack:
            stack.enter_context(unittest.mock.patch(
                "tempfile.NamedTemporaryFile",
                new=base.NamedTemporaryFile
            ))

            stack.enter_context(unittest.mock.patch(
                "os.replace",
                new=base.replace
            ))

            stack.enter_context(unittest.mock.patch(
                "os.unlink",
                new=base.unlink
            ))

            stack.enter_context(unittest.mock.patch(
                "aioxmpp.xml.XMPPXMLGenerator",
                new=base.XMPPXMLGenerator
            ))

            stack.enter_context(unittest.mock.patch(
                "aioxmpp.xso.events_to_sax",
                new=base.events_to_sax
            ))

            stack.enter_context(unittest.mock.patch(
                "aioxmpp.utils.mkdir_exist_ok",
                new=base.mkdir_exist_ok,
            ))

            entitycaps_service.writeback(base.p,
                                         base.data)

        calls = list(base.mock_calls)
        self.assertSequenceEqual(
            calls,
            [
                unittest.mock.call.mkdir_exist_ok(base.p.parent),
                unittest.mock._Call(("p.parent.__str__", (), {})),
                unittest.mock.call.NamedTemporaryFile(
                    dir=str(base.p.parent),
                    delete=False
                ),
                unittest.mock.call.NamedTemporaryFile().__enter__(),
                unittest.mock.call.XMPPXMLGenerator(
                    base.NamedTemporaryFile().__enter__(),
                    short_empty_elements=True,
                ),
                unittest.mock.call.XMPPXMLGenerator().startDocument(),
                unittest.mock.call.events_to_sax(
                    base.data,
                    base.XMPPXMLGenerator()
                ),
                unittest.mock.call.XMPPXMLGenerator().endDocument(),
                unittest.mock.call.NamedTemporaryFile().__exit__(
                    None, None, None
                ),
                unittest.mock._Call(("p.__str__", (), {})),
                unittest.mock.call.replace(
                    base.NamedTemporaryFile().__enter__().name,
                    str(base.p),
                ),
            ]
        )

    def test_unlinks_tempfile_on_error(self):
        base = unittest.mock.Mock()
        base.p = unittest.mock.MagicMock()
        base.NamedTemporaryFile = unittest.mock.MagicMock()

        with contextlib.ExitStack() as stack:
            stack.enter_context(unittest.mock.patch(
                "tempfile.NamedTemporaryFile",
                new=base.NamedTemporaryFile
            ))

            stack.enter_context(unittest.mock.patch(
                "os.replace",
                new=base.replace
            ))

            stack.enter_context(unittest.mock.patch(
                "os.unlink",
                new=base.unlink
            ))

            stack.enter_context(unittest.mock.patch(
                "aioxmpp.xml.XMPPXMLGenerator",
                new=base.XMPPXMLGenerator
            ))

            stack.enter_context(unittest.mock.patch(
                "aioxmpp.xso.events_to_sax",
                new=base.events_to_sax
            ))

            stack.enter_context(unittest.mock.patch(
                "aioxmpp.utils.mkdir_exist_ok",
                new=base.mkdir_exist_ok,
            ))

            exc = Exception()
            base.events_to_sax.side_effect = exc

            with self.assertRaises(Exception) as ctx:
                entitycaps_service.writeback(
                    base.p,
                    base.data)

        self.assertIs(ctx.exception, exc)

        calls = list(base.mock_calls)
        self.assertSequenceEqual(
            calls,
            [
                unittest.mock.call.mkdir_exist_ok(base.p.parent),
                unittest.mock._Call(("p.parent.__str__", (), {})),
                unittest.mock.call.NamedTemporaryFile(
                    dir=str(base.p.parent),
                    delete=False
                ),
                unittest.mock.call.NamedTemporaryFile().__enter__(),
                unittest.mock.call.XMPPXMLGenerator(
                    base.NamedTemporaryFile().__enter__(),
                    short_empty_elements=True,
                ),
                unittest.mock.call.XMPPXMLGenerator().startDocument(),
                unittest.mock.call.events_to_sax(
                    base.data,
                    base.XMPPXMLGenerator()
                ),
                unittest.mock.call.unlink(
                    base.NamedTemporaryFile().__enter__().name
                ),
                unittest.mock.call.NamedTemporaryFile().__exit__(
                    unittest.mock.ANY,
                    unittest.mock.ANY,
                    unittest.mock.ANY,
                ),
            ]
        )

# foo
