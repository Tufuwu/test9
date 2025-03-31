# Copyright (C) Linaro Limited 2015
# Author: Milo Casagrande <milo.casagrande@linaro.org>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""Test module for the JobHandler handler."""

try:
    import simplejson as json
except ImportError:
    import json

import tornado

import urls

from handlers.tests.test_handler_base import TestHandlerBase


class TestStatsHandler(TestHandlerBase):

    def get_app(self):
        return tornado.web.Application([urls._STATS_URL], **self.settings)

    def test_post(self):
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps({"foo": "bar"})

        response = self.fetch(
            "/statistics", method="POST", headers=headers, body=body)

        self.assertEqual(response.code, 501)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_post_wrong_token(self):
        self.validate_token.return_value = (False, None)
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps({"foo": "bar"})

        response = self.fetch(
            "/statistics", method="POST", headers=headers, body=body)

        self.assertEqual(response.code, 403)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_put(self):
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps({"foo": "bar"})

        response = self.fetch(
            "/statistics", method="PUT", headers=headers, body=body)

        self.assertEqual(response.code, 501)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_put_wrong_token(self):
        self.validate_token.return_value = (False, None)
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps({"foo": "bar"})

        response = self.fetch(
            "/statistics", method="PUT", headers=headers, body=body)

        self.assertEqual(response.code, 403)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_delete(self):
        headers = {"Authorization": "foo"}

        response = self.fetch(
            "/statistics", method="DELETE", headers=headers)

        self.assertEqual(response.code, 501)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_delete_wrong_token(self):
        self.validate_token.return_value = (False, None)
        headers = {"Authorization": "foo"}

        response = self.fetch("/statistics", method="DELETE", headers=headers)

        self.assertEqual(response.code, 403)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)
