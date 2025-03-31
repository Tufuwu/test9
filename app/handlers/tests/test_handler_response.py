# Copyright (C) Linaro Limited 2014,2015
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

"""Test class for HandlerResponse object."""

import unittest

import handlers.response as hresponse


class TestHandlerResponse(unittest.TestCase):

    def test_response_constructor_not_valid_input(self):
        self.assertRaises(ValueError, hresponse.HandlerResponse, "1")

    def test_response_setter_not_valid(self):
        response = hresponse.HandlerResponse()

        def _setter_call(value):
            response.status_code = value

        self.assertRaises(ValueError, _setter_call, "1")
        self.assertRaises(ValueError, _setter_call, [1])
        self.assertRaises(ValueError, _setter_call, {})
        self.assertRaises(ValueError, _setter_call, ())

    def test_response_setter_valid(self):
        response = hresponse.HandlerResponse(1)
        response.status_code = 200

        self.assertEqual(response.status_code, 200)

    def test_reponse_creation_default_values(self):
        response = hresponse.HandlerResponse()

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.headers)
        self.assertIsNone(response.result)
        self.assertIsNone(response.reason)

    def test_response_reason_setter_valid(self):
        response = hresponse.HandlerResponse()

        response.reason = u'foo'
        self.assertEqual('foo', response.reason)

        response.reason = r'bar'
        self.assertEqual('bar', response.reason)

    def test_response_reason_setter_not_valid(self):
        response = hresponse.HandlerResponse()

        def _setter_call(value):
            response.reason = value

        self.assertRaises(ValueError, _setter_call, [1])
        self.assertRaises(ValueError, _setter_call, {})
        self.assertRaises(ValueError, _setter_call, ())

    def test_response_count_setter_not_valid(self):
        response = hresponse.HandlerResponse()

        def _setter_call(value):
            response.count = value

        self.assertRaises(ValueError, _setter_call, "1")
        self.assertRaises(ValueError, _setter_call, [1])
        self.assertRaises(ValueError, _setter_call, {})
        self.assertRaises(ValueError, _setter_call, ())

    def test_response_limit_setter_not_valid(self):
        response = hresponse.HandlerResponse()

        def _setter_call(value):
            response.limit = value

        self.assertRaises(ValueError, _setter_call, "1")
        self.assertRaises(ValueError, _setter_call, [1])
        self.assertRaises(ValueError, _setter_call, {})
        self.assertRaises(ValueError, _setter_call, ())

    def test_response_errors_setter_valid(self):
        response = hresponse.HandlerResponse()
        response.errors = "1 error"

        self.assertEqual(response.errors, ["1 error"])

        response.errors = ["2 errors", "3 errors"]
        self.assertEqual(response.errors, ["1 error", "2 errors", "3 errors"])

    def test_response_result_setter(self):
        response = hresponse.HandlerResponse()

        response.result = {}
        self.assertIsInstance(response.result, list)
        self.assertEqual(response.result, [{}])

        response.result = 1
        self.assertIsInstance(response.result, list)
        self.assertEqual(response.result, [1])

        response.result = u'foo'
        self.assertIsInstance(response.result, list)
        self.assertEqual(response.result, ['foo'])

    def test_response_headers_setter_not_valid(self):
        response = hresponse.HandlerResponse()

        def _setter_call(value):
            response.headers = value

        self.assertRaises(ValueError, _setter_call, 1)
        self.assertRaises(ValueError, _setter_call, True)
        self.assertRaises(ValueError, _setter_call, [])
        self.assertRaises(ValueError, _setter_call, ())
        self.assertRaises(ValueError, _setter_call, "1")

    def test_response_headers_setter_valid(self):
        response = hresponse.HandlerResponse()

        response.headers = {'foo': 'bar'}
        self.assertEqual({'foo': 'bar'}, response.headers)

    def test_response_messages_setter(self):
        response = hresponse.HandlerResponse()
        response.messages = "A message"
        response.messages = None

        expected = ["A message"]
        self.assertListEqual(expected, response.messages)

    def test_response_messages_setter_with_list(self):
        response = hresponse.HandlerResponse()
        response.messages = "A message"
        response.messages = ["1 message", "2 messages"]

        expected = ["A message", "1 message", "2 messages"]
        self.assertListEqual(expected, response.messages)
