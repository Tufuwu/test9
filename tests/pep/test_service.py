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
import contextlib
import gc
import unittest
import unittest.mock

import aioxmpp
import aioxmpp.forms
import aioxmpp.disco.xso as disco_xso
import aioxmpp.pep as pep
import aioxmpp.pep.service as pep_service
import aioxmpp.pubsub.xso as pubsub_xso

from aioxmpp.testutils import (
    make_connected_client,
    CoroutineMock,
    run_coroutine,
)


TEST_FROM = aioxmpp.structs.JID.fromstr("foo@bar.example/baz")
TEST_JID1 = aioxmpp.structs.JID.fromstr("bar@bar.example/baz")


class TestPEPClient(unittest.TestCase):

    def setUp(self):
        self.cc = make_connected_client()
        self.cc.local_jid = TEST_FROM

        self.disco_client = aioxmpp.DiscoClient(self.cc)
        self.disco_server = aioxmpp.DiscoServer(self.cc)
        self.pubsub = aioxmpp.PubSubClient(self.cc, dependencies={
            aioxmpp.DiscoClient: self.disco_client
        })

        self.s = pep.PEPClient(self.cc, dependencies={
            aioxmpp.DiscoClient: self.disco_client,
            aioxmpp.DiscoServer: self.disco_server,
            aioxmpp.PubSubClient: self.pubsub,
        })

    def tearDown(self):
        del self.cc
        del self.disco_client
        del self.disco_server
        del self.pubsub
        del self.s

    def test_is_service(self):
        self.assertTrue(issubclass(pep.PEPClient, aioxmpp.service.Service))

    def test_depends_on_entity_caps(self):
        self.assertIn(
            aioxmpp.EntityCapsService,
            pep.PEPClient.ORDER_AFTER,
        )

    def test_depends_on_pubsub(self):
        self.assertIn(
            aioxmpp.PubSubClient,
            pep.PEPClient.ORDER_AFTER,
        )

    def test_check_for_pep(self):
        disco_info = disco_xso.InfoQuery()
        disco_info.identities.append(
            disco_xso.Identity(type_="pep", category="pubsub")
        )

        with unittest.mock.patch.object(
                self.disco_client, "query_info",
                new=CoroutineMock()) as query_info_mock:
            query_info_mock.return_value = disco_info
            run_coroutine(self.s._check_for_pep())
        query_info_mock.assert_called_once_with(
            TEST_FROM.bare()
        )

    def test_check_for_pep_failure(self):
        with unittest.mock.patch.object(
                self.disco_client, "query_info",
                new=CoroutineMock()) as query_info_mock:
            self.disco_client.query_info.return_value = disco_xso.InfoQuery()

            with self.assertRaises(RuntimeError):
                run_coroutine(self.s._check_for_pep())

        query_info_mock.assert_called_once_with(
            TEST_FROM.bare()
        )

    def test_handle_pubsub_publish_is_depsignal_handler(self):
        self.assertTrue(aioxmpp.service.is_depsignal_handler(
            aioxmpp.PubSubClient,
            "on_item_published",
            self.s._handle_pubsub_publish
        ))

    def test_publish(self):
        with contextlib.ExitStack() as stack:
            check_for_pep_mock = stack.enter_context(
                unittest.mock.patch.object(
                    self.s,
                    "_check_for_pep",
                    CoroutineMock(),
                )
            )

            publish_mock = stack.enter_context(
                unittest.mock.patch.object(
                    self.pubsub,
                    "publish",
                    CoroutineMock(),
                )
            )

            run_coroutine(self.s.publish(
                "urn:example",
                unittest.mock.sentinel.data,
                id_="example-id",
            ))

        check_for_pep_mock.assert_called_once_with()
        publish_mock.assert_called_once_with(
            None,
            "urn:example",
            unittest.mock.sentinel.data,
            id_="example-id",
            publish_options=None,
        )

    def test_publish_with_access_model(self):
        with contextlib.ExitStack() as stack:
            check_for_pep_mock = stack.enter_context(
                unittest.mock.patch.object(
                    self.s,
                    "_check_for_pep",
                    CoroutineMock(),
                )
            )

            publish_mock = stack.enter_context(
                unittest.mock.patch.object(
                    self.pubsub,
                    "publish",
                    CoroutineMock(),
                )
            )

            run_coroutine(self.s.publish(
                "urn:example",
                unittest.mock.sentinel.data,
                id_="example-id",
                access_model="foobar",
            ))

        check_for_pep_mock.assert_called_once_with()
        publish_mock.assert_called_once_with(
            None,
            "urn:example",
            unittest.mock.sentinel.data,
            id_="example-id",
            publish_options=unittest.mock.ANY,
        )

        _, _, kwargs = publish_mock.mock_calls[-1]

        publish_options = kwargs.pop("publish_options")

        self.assertIsInstance(publish_options, aioxmpp.forms.Data)
        self.assertEqual(publish_options.get_form_type(),
                         "http://jabber.org/protocol/pubsub#publish-options")
        self.assertEqual(len(publish_options.fields), 2)
        self.assertEqual(publish_options.fields[1].var, "pubsub#access_model")
        self.assertCountEqual(publish_options.fields[1].values,
                              ["foobar"])

    def test_claim_pep_node_twice(self):
        handler1 = unittest.mock.Mock()
        handler2 = unittest.mock.Mock()
        with unittest.mock.patch.object(
                self.disco_server,
                "register_feature") as register_feature_mock:
            claim = self.s.claim_pep_node("urn:example")
            claim.on_item_publish.connect(handler1)
            register_feature_mock.assert_called_once_with("urn:example")
            with self.assertRaisesRegex(
                    RuntimeError,
                    "^claiming already claimed node$"):
                claim2 = self.s.claim_pep_node("urn:example")
                claim2.on_item_publish.connect(handler2)
            # register feature mock was not called a second time
            self.assertEqual(len(register_feature_mock.mock_calls), 1)
        with unittest.mock.patch.object(
                self.disco_server,
                "unregister_feature") as unregister_feature_mock:
            claim.close()
        unregister_feature_mock.assert_called_once_with("urn:example")

    def test_claim_pep_node_handle_event_unclaim_pep_node(self):
        handler = unittest.mock.Mock()
        with unittest.mock.patch.object(
                self.disco_server,
                "register_feature") as register_feature_mock:
            claim = self.s.claim_pep_node("urn:example")
            claim.on_item_publish.connect(handler)

        register_feature_mock.assert_called_once_with(
            "urn:example"
        )

        registered = unittest.mock.Mock()
        registered.TAG = "urn:example", "example"
        payload = unittest.mock.Mock()
        payload.registered_payload = registered

        self.s._handle_pubsub_publish(
            TEST_JID1,
            "urn:example",
            payload,
            message=None
        )

        handler.assert_called_once_with(
            TEST_JID1,
            "urn:example",
            payload,
            message=None
        )

        with unittest.mock.patch.object(
                self.disco_server,
                "unregister_feature") as unregister_feature_mock:
            claim.close()

        unregister_feature_mock.assert_called_once_with(
            "urn:example"
        )

        handler.reset_mock()

        self.s._handle_pubsub_publish(
            TEST_JID1,
            "urn:example",
            payload,
            message=None
        )

        self.assertEqual(len(handler.mock_calls), 0)

    def test_handle_event_filters_empty_notify(self):

        handler = unittest.mock.Mock()
        with unittest.mock.patch.object(
                self.disco_server,
                "register_feature") as register_feature_mock:
            claim = self.s.claim_pep_node("urn:example")
            claim.on_item_publish.connect(handler)

        register_feature_mock.assert_called_once_with(
            "urn:example"
        )

        payload = pubsub_xso.EventItem(None)

        self.s._handle_pubsub_publish(
            TEST_JID1,
            "urn:example",
            payload,
            message=None
        )

        self.assertEqual(len(handler.mock_calls), 0)

        with unittest.mock.patch.object(
                self.disco_server,
                "unregister_feature") as unregister_feature_mock:
            claim.close()

        unregister_feature_mock.assert_called_once_with(
            "urn:example"
        )

    def test_handle_event_filters_malformed_notify(self):

        handler = unittest.mock.Mock()
        with unittest.mock.patch.object(
                self.disco_server,
                "register_feature") as register_feature_mock:
            claim = self.s.claim_pep_node("urn:example")
            claim.on_item_publish.connect(handler)

        register_feature_mock.assert_called_once_with(
            "urn:example"
        )

        registered = unittest.mock.Mock()
        registered.TAG = "urn:example:2", "example"
        payload = unittest.mock.Mock()
        payload.registered_payload = registered

        self.s._handle_pubsub_publish(
            TEST_JID1,
            "urn:example",
            payload,
            message=None
        )

        self.assertEqual(len(handler.mock_calls), 0)

        with unittest.mock.patch.object(
                self.disco_server,
                "unregister_feature") as unregister_feature_mock:
            claim.close()

        unregister_feature_mock.assert_called_once_with(
            "urn:example"
        )

    def test_claim_pep_node_with_notify(self):
        handler = unittest.mock.Mock()
        with unittest.mock.patch.object(
                self.disco_server,
                "register_feature") as register_feature_mock:
            claim = self.s.claim_pep_node("urn:example", notify=True)
            claim.on_item_publish.connect(handler)

        self.assertCountEqual(
            register_feature_mock.mock_calls,
            [unittest.mock.call("urn:example+notify"),
             unittest.mock.call("urn:example")]
        )

        with unittest.mock.patch.object(
                self.disco_server,
                "unregister_feature") as unregister_feature_mock:
            claim.close()

        self.assertCountEqual(
            unregister_feature_mock.mock_calls,
            [unittest.mock.call("urn:example+notify"),
             unittest.mock.call("urn:example")]
        )

        self.assertEqual(len(handler.mock_calls), 0)

    def test_claim_pep_node_no_feature(self):
        handler = unittest.mock.Mock()
        with unittest.mock.patch.object(
                self.disco_server,
                "register_feature") as register_feature_mock:
            claim = self.s.claim_pep_node("urn:example",
                                          register_feature=False)
            claim.on_item_publish.connect(handler)
        register_feature_mock.assert_not_called()

        with unittest.mock.patch.object(
                self.disco_server,
                "unregister_feature") as unregister_feature_mock:
            claim.close()

        self.assertEqual(len(unregister_feature_mock.mock_calls), 0)
        self.assertEqual(len(handler.mock_calls), 0)

    def test_closed_claim(self):
        claim = self.s.claim_pep_node("urn:example")
        claim.close()

        with self.assertRaises(RuntimeError):
            claim.notify = True

        with self.assertRaises(RuntimeError):
            claim.feature_registered = True

    def test_claim_attributes(self):
        with contextlib.ExitStack() as stack:

            register_feature_mock = stack.enter_context(
                unittest.mock.patch.object(
                    self.disco_server, "register_feature"))

            unregister_feature_mock = stack.enter_context(
                unittest.mock.patch.object(
                    self.disco_server, "unregister_feature"))

            claim = self.s.claim_pep_node("urn:example")
            register_feature_mock.assert_called_once_with("urn:example")
            register_feature_mock.reset_mock()
            self.assertFalse(claim.notify)
            self.assertTrue(claim.feature_registered)
            claim.notify = True
            register_feature_mock.assert_called_once_with("urn:example+notify")
            register_feature_mock.reset_mock()
            self.assertTrue(claim.notify)
            claim.notify = True
            self.assertTrue(claim.notify)
            self.assertEqual(len(register_feature_mock.mock), 0)
            register_feature_mock.reset_mock()
            claim.notify = False
            self.assertFalse(claim.notify)
            unregister_feature_mock.assert_called_once_with(
                "urn:example+notify"
            )
            unregister_feature_mock.reset_mock()
            claim.notify = False
            self.assertFalse(claim.notify)
            self.assertEqual(len(register_feature_mock.mock), 0)
            unregister_feature_mock.reset_mock()

            self.assertTrue(claim.feature_registered)
            claim.feature_registered = True
            self.assertEqual(len(register_feature_mock.mock), 0)
            register_feature_mock.reset_mock()
            self.assertTrue(claim.feature_registered)
            claim.feature_registered = False
            self.assertFalse(claim.feature_registered)
            unregister_feature_mock.assert_called_once_with("urn:example")
            unregister_feature_mock.reset_mock()
            claim.feature_registered = False
            self.assertFalse(claim.feature_registered)
            self.assertEqual(len(register_feature_mock.mock), 0)
            unregister_feature_mock.reset_mock()
            claim.feature_registered = True
            self.assertTrue(claim.feature_registered)
            register_feature_mock.assert_called_once_with("urn:example")
            register_feature_mock.reset_mock()

    def test_close_is_idempotent(self):
        claim = self.s.claim_pep_node("urn:example")
        claim.close()
        self.assertTrue(claim._closed)

        class Token:
            _closed = True

            def __setattr__(myself, attr, value):
                self.fail("setting attr")

            def __getattr__(myself, attr, value):
                self.fail("getting attr")

        pep_service.RegisteredPEPNode.close(Token())

    def test_is_claimed(self):
        claim = self.s.claim_pep_node("urn:example")
        self.assertTrue(self.s.is_claimed("urn:example"))
        claim.close()
        self.assertFalse(self.s.is_claimed("urn:example"))

    def test_weakref_magic_works(self):
        self.s.claim_pep_node("urn:example")

        # trigger a garbage collection to ensure the pep node weakref
        # is reaped – while this is not necessary on CPython it might
        # be necessary on other implementations
        gc.collect()

        self.assertFalse(self.s.is_claimed("urn:example"))


class ExampleService(aioxmpp.service.Service):

    ORDER_AFTER = [
        aioxmpp.pep.PEPClient
    ]

    _claim_1 = aioxmpp.pep.register_pep_node(
        "urn:example:register_pep_node_example:1",
    )

    _claim_2 = aioxmpp.pep.register_pep_node(
        "urn:example:register_pep_node_example:2",
        notify=True,
    )

    _claim_3 = aioxmpp.pep.register_pep_node(
        "urn:example:register_pep_node_example:3",
        register_feature=False,
    )

    _claim_4 = aioxmpp.pep.register_pep_node(
        "urn:example:register_pep_node_example:4",
        notify=True, register_feature=False,
    )

    def __init__(self, client, **kwargs):
        super().__init__(client, **kwargs)


class Test_register_pep_node(unittest.TestCase):

    def setUp(self):
        self.cc = make_connected_client()
        self.cc.local_jid = TEST_FROM

        self.disco_client = aioxmpp.DiscoClient(self.cc)
        self.disco_server = aioxmpp.DiscoServer(self.cc)
        self.pubsub = aioxmpp.PubSubClient(self.cc, dependencies={
            aioxmpp.DiscoClient: self.disco_client
        })

        self.pep = pep.PEPClient(self.cc, dependencies={
            aioxmpp.DiscoClient: self.disco_client,
            aioxmpp.DiscoServer: self.disco_server,
            aioxmpp.PubSubClient: self.pubsub,
        })

        self.s = ExampleService(self.cc, dependencies={
            pep.PEPClient: self.pep,
        })

    def tearDown(self):
        del self.cc
        del self.disco_client
        del self.disco_server
        del self.pubsub
        del self.pep

        # ensure the clients are collected
        gc.collect()

    def test_value_type(self):
        self.assertIs(
            ExampleService._claim_1.value_type,
            pep_service.RegisteredPEPNode,
        )

    def test_config(self):
        self.assertEqual(
            ExampleService._claim_1.node_namespace,
            "urn:example:register_pep_node_example:1"
        )
        self.assertFalse(ExampleService._claim_1.notify)
        self.assertTrue(ExampleService._claim_1.register_feature)

        self.assertEqual(
            ExampleService._claim_2.node_namespace,
            "urn:example:register_pep_node_example:2"
        )
        self.assertTrue(ExampleService._claim_2.notify)
        self.assertTrue(ExampleService._claim_2.register_feature)

        self.assertEqual(
            ExampleService._claim_3.node_namespace,
            "urn:example:register_pep_node_example:3"
        )
        self.assertFalse(ExampleService._claim_3.notify)
        self.assertFalse(ExampleService._claim_3.register_feature)

        self.assertEqual(
            ExampleService._claim_4.node_namespace,
            "urn:example:register_pep_node_example:4"
        )
        self.assertTrue(ExampleService._claim_4.notify)
        self.assertFalse(ExampleService._claim_4.register_feature)

    def test_claims(self):
        self.pep.is_claimed("urn:example:register_pep_node_example:1")
        self.assertIsInstance(self.s._claim_1,
                              aioxmpp.pep.service.RegisteredPEPNode)
        self.assertFalse(self.s._claim_1.notify)
        self.assertTrue(self.s._claim_1.feature_registered)

        self.pep.is_claimed("urn:example:register_pep_node_example:2")
        self.assertIsInstance(self.s._claim_2,
                              aioxmpp.pep.service.RegisteredPEPNode)
        self.assertTrue(self.s._claim_2.notify)
        self.assertTrue(self.s._claim_2.feature_registered)

        self.pep.is_claimed("urn:example:register_pep_node_example:3")
        self.assertIsInstance(self.s._claim_3,
                              aioxmpp.pep.service.RegisteredPEPNode)
        self.assertFalse(self.s._claim_3.notify)
        self.assertFalse(self.s._claim_3.feature_registered)

        self.pep.is_claimed("urn:example:register_pep_node_example:4")
        self.assertIsInstance(self.s._claim_4,
                              aioxmpp.pep.service.RegisteredPEPNode)
        self.assertTrue(self.s._claim_4.notify)
        self.assertFalse(self.s._claim_4.feature_registered)
