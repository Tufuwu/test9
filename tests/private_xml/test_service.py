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

import aioxmpp
import aioxmpp.private_xml.service as private_xml_service
import aioxmpp.private_xml.xso as private_xml_xso

from aioxmpp.testutils import (
    make_connected_client,
    CoroutineMock,
    run_coroutine,
)


@private_xml_xso.Query.as_payload_class
class FakePayload(aioxmpp.xso.XSO):
    TAG = "tests/private_xml/test_service.py", "payload"


class TestService(unittest.TestCase):

    def setUp(self):
        self.cc = make_connected_client()
        self.s = private_xml_service.PrivateXMLService(
            self.cc,
            dependencies={},
        )
        self.cc.mock_calls.clear()

    def tearDown(self):
        del self.cc
        del self.s

    def test_is_service(self):
        self.assertTrue(issubclass(
            private_xml_service.PrivateXMLService,
            aioxmpp.service.Service
        ))

    def test_get_private_xml(self):
        payload = FakePayload()

        with unittest.mock.patch.object(self.cc, "send",
                                        new=CoroutineMock()) as mock_send:
            mock_send.return_value = unittest.mock.sentinel.result
            res = run_coroutine(self.s.get_private_xml(payload))

        self.assertEqual(len(mock_send.mock_calls), 1)
        try:
            (_, (arg,), kwargs), = mock_send.mock_calls
        except ValueError:
            self.fail("send called with wrong signature")
        self.assertEqual(len(kwargs), 0)
        self.assertIsInstance(arg, aioxmpp.IQ)
        self.assertEqual(arg.type_, aioxmpp.IQType.GET)
        self.assertIsInstance(arg.payload, private_xml_xso.Query)
        self.assertEqual(arg.payload.registered_payload, payload)

        self.assertEqual(res, unittest.mock.sentinel.result)

    def test_set_private_xml(self):
        payload = FakePayload()

        with unittest.mock.patch.object(self.cc, "send",
                                        new=CoroutineMock()) as mock_send:
            run_coroutine(self.s.set_private_xml(payload))

        self.assertEqual(len(mock_send.mock_calls), 1)
        try:
            (_, (arg,), kwargs), = mock_send.mock_calls
        except ValueError:
            self.fail("send called with wrong signature")
        self.assertEqual(len(kwargs), 0)
        self.assertIsInstance(arg, aioxmpp.IQ)
        self.assertEqual(arg.type_, aioxmpp.IQType.SET)
        self.assertIsInstance(arg.payload, private_xml_xso.Query)
        self.assertEqual(arg.payload.registered_payload, payload)
