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

import aioxmpp.disco
import aioxmpp.shim.service as shim_service

from aioxmpp.testutils import (
    make_connected_client,
    CoroutineMock,
    run_coroutine,
)

TEST_FROM = aioxmpp.structs.JID.fromstr("foo@bar.example/baz")


class TestService(unittest.TestCase):
    def setUp(self):
        self.disco = unittest.mock.Mock()
        self.disco.query_info = CoroutineMock()
        self.disco.query_info.side_effect = AssertionError
        self.disco.query_items = CoroutineMock()
        self.disco.query_items.side_effect = AssertionError
        self.node = unittest.mock.Mock()
        self.cc = make_connected_client()
        self.cc.local_jid = TEST_FROM

        with unittest.mock.patch("aioxmpp.disco.StaticNode") as Node:
            Node.return_value = self.node
            self.s = shim_service.SHIMService(self.cc, dependencies={
                aioxmpp.DiscoServer: self.disco
            })

        self.disco.mock_calls.clear()
        self.cc.mock_calls.clear()

    def tearDown(self):
        del self.s
        del self.cc
        del self.disco

    def test_orders_before_disco_service(self):
        self.assertIn(
            aioxmpp.DiscoServer,
            shim_service.SHIMService.ORDER_AFTER,
        )

    def test_init(self):
        self.disco = unittest.mock.Mock()
        self.disco.query_info = CoroutineMock()
        self.disco.query_info.side_effect = AssertionError
        self.disco.query_items = CoroutineMock()
        self.disco.query_items.side_effect = AssertionError
        self.cc = make_connected_client()
        self.cc.local_jid = TEST_FROM

        with unittest.mock.patch("aioxmpp.disco.StaticNode") as Node:
            self.s = shim_service.SHIMService(self.cc, dependencies={
                aioxmpp.DiscoServer: self.disco,
            })

        self.disco.register_feature.assert_called_with(
            "http://jabber.org/protocol/shim"
        )

        self.disco.mount_node.assert_called_with(
            "http://jabber.org/protocol/shim",
            Node()
        )

    def test_shutdown(self):
        run_coroutine(self.s.shutdown())
        self.disco.unregister_feature.assert_called_with(
            "http://jabber.org/protocol/shim"
        )

        self.disco.unmount_node.assert_called_with(
            "http://jabber.org/protocol/shim",
        )

    def test_register_header(self):
        self.s.register_header(
            "Foo"
        )

        self.node.register_feature.assert_called_with(
            "http://jabber.org/protocol/shim#Foo"
        )

    def test_unregister_header(self):
        self.s.unregister_header(
            "Foo"
        )

        self.node.unregister_feature.assert_called_with(
            "http://jabber.org/protocol/shim#Foo"
        )
