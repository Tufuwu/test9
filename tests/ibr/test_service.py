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
import unittest
import unittest.mock
import aioxmpp
import asyncio

import aioxmpp.ibr.service as ibr_service
import aioxmpp.ibr.xso as ibr_xso

from aioxmpp.testutils import (
    make_connected_client,
    run_coroutine,
    CoroutineMock
)


TEST_PEER = aioxmpp.JID.fromstr("juliet@capulet.lit/balcony")


class TestService(unittest.TestCase):

    def setUp(self):
        self.cc = make_connected_client()
        self.s = ibr_service.RegistrationService(self.cc)

    def test_ibr_get_client_info(self):
        query = ibr_xso.Query()
        query.username = TEST_PEER.localpart
        self.cc.send.return_value = query
        self.cc.local_jid = TEST_PEER

        res = run_coroutine(self.s.get_client_info())

        self.cc.send.assert_called_once_with(unittest.mock.ANY)

        _, (iq, ), _ = self.cc.send.mock_calls[0]

        self.assertIsInstance(
            iq,
            aioxmpp.IQ,
        )

        self.assertEqual(
            iq.to,
            TEST_PEER.bare().replace(localpart=None),
        )

        self.assertEqual(
            iq.type_,
            aioxmpp.IQType.GET,
        )

        self.assertIsInstance(
            iq.payload,
            ibr_xso.Query,
        )

        self.assertIsInstance(
            res,
            ibr_xso.Query,
        )

        self.assertEqual(
            res.username,
            TEST_PEER.localpart,
        )

    def test_ibr_change_pass(self):
        self.cc.local_jid = TEST_PEER
        new_pass = "aaa"

        run_coroutine(
            self.s.change_pass(new_pass)
        )

        self.cc.send.assert_called_once_with(unittest.mock.ANY)

        _, (iq, ), _ = self.cc.send.mock_calls[0]

        self.assertIsInstance(
            iq,
            aioxmpp.IQ,
        )

        self.assertEqual(
            iq.type_,
            aioxmpp.IQType.SET,
        )

        self.assertEqual(
            iq.to,
            TEST_PEER.bare().replace(localpart=None),
        )

        self.assertIsInstance(
            iq.payload,
            ibr_xso.Query,
        )

        self.assertEqual(
            iq.payload.username,
            TEST_PEER.localpart,
        )

        self.assertEqual(
            iq.payload.password,
            new_pass,
        )

    def test_ibr_cancel_registration(self):
        self.cc.local_jid = TEST_PEER

        run_coroutine(self.s.cancel_registration())

        self.cc.send.assert_called_once_with(unittest.mock.ANY)

        _, (iq, ), _ = self.cc.send.mock_calls[0]

        self.assertIsInstance(
            iq,
            aioxmpp.IQ,
        )

        self.assertEqual(
            iq.to,
            TEST_PEER.bare().replace(localpart=None),
        )

        self.assertEqual(
            iq.type_,
            aioxmpp.IQType.SET,
        )

        self.assertIsInstance(
            iq.payload,
            ibr_xso.Query,
        )

        self.assertEqual(
            iq.payload.remove,
            True,
        )

    def test_ibr_get_registration_fields(self):
        with unittest.mock.patch(
                'aioxmpp.protocol.send_and_wait_for',
                new=CoroutineMock()
        ) as mock1:
            iq_res = aioxmpp.IQ(
                type_=aioxmpp.IQType.GET,
                payload=ibr_xso.Query()
            )
            iq_res.payload.username = ''
            mock1.return_value = iq_res
            stream = unittest.mock.Mock(spec=aioxmpp.protocol.XMLStream)
            stream._to = TEST_PEER.domain
            res = run_coroutine(aioxmpp.ibr.get_registration_fields(stream))

            _, (_, iq, *_), _ = mock1.mock_calls[0]

            iq = iq[0]

            self.assertIsInstance(
                iq,
                aioxmpp.IQ,
            )

            self.assertIs(
                iq_res.payload,
                res,
            )

            self.assertIsInstance(
                res,
                ibr_xso.Query,
            )

            self.assertEqual(
                res.username,
                '',
            )

    def test_ibr_register(self):
        password = "aaa"
        aux_fields = {"nick": "romeo's lover"}
        with unittest.mock.patch(
                'aioxmpp.protocol.send_and_wait_for',
                new=CoroutineMock()
        ) as mock1:
            stream = unittest.mock.Mock(spec=aioxmpp.protocol.XMLStream)
            stream._to = TEST_PEER.domain
            query = aioxmpp.ibr.Query(TEST_PEER.localpart, "aaa", aux_fields)
            run_coroutine(aioxmpp.ibr.register(stream, query))

            _, (_, iq, *_), _ = mock1.mock_calls[0]

            iq = iq[0]

            self.assertIsInstance(
                iq,
                aioxmpp.IQ,
            )

            self.assertEqual(
                iq.to,
                TEST_PEER.bare().replace(localpart=None),
            )

            self.assertEqual(
                iq.type_,
                aioxmpp.IQType.SET,
            )

            self.assertIsInstance(
                iq.payload,
                ibr_xso.Query,
            )

            self.assertEqual(
                iq.payload.username,
                TEST_PEER.localpart,
            )

            self.assertEqual(
                iq.payload.password,
                password,
            )

            if aux_fields is not None:
                for key, value in aux_fields.items():
                    self.assertEqual(
                        getattr(iq.payload, key),
                        value,
                    )


if __name__ == '__main__':
    unittest.main()
