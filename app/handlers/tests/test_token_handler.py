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

"""Test module for the TokenHandler handler."""

import json
import mock
import tornado

import urls

from handlers.tests.test_handler_base import TestHandlerBase


class TestTokenHandler(TestHandlerBase):

    def get_app(self):
        return tornado.web.Application([urls._TOKEN_URL], **self.settings)

    def test_get_no_token(self):
        response = self.fetch("/token")

        self.assertEqual(response.code, 403)

    def test_get_wrong_token(self):
        self.validate_token.return_value = (False, None)
        headers = {"Authorization": "foo"}
        response = self.fetch("/token", headers=headers)

        self.assertEqual(response.code, 403)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    @mock.patch("utils.db.find")
    @mock.patch("utils.db.count")
    def test_get_with_master_key(self, mock_count, mock_find):
        mock_count.return_value = 0
        mock_find.return_value = []

        headers = {"Authorization": "bar"}
        response = self.fetch("/token", headers=headers)

        self.assertEqual(response.code, 200)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    @mock.patch("utils.db.find")
    @mock.patch("utils.db.count")
    def test_get(self, mock_count, mock_find):
        mock_count.return_value = 0
        mock_find.return_value = []

        expected_body = {
            "count": 0,
            "code": 200,
            "limit": 0,
            "skip": 0,
            "result": []
        }

        headers = {"Authorization": "foo"}
        response = self.fetch("/token", headers=headers)

        self.assertEqual(response.code, 200)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)
        self.assertDictEqual(json.loads(response.body), expected_body)

    @mock.patch("utils.db.find_one2")
    def test_get_one(self, mock_find):
        mock_find.return_value = {"token": "foo"}

        headers = {"Authorization": "foo"}
        response = self.fetch("/token/foo", headers=headers)

        self.assertEqual(response.code, 200)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_post_without_token(self):
        body = json.dumps(dict(email="foo"))

        response = self.fetch("/token", method="POST", body=body)

        self.assertEqual(response.code, 403)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_post_wrong_content_type(self):
        headers = {"Authorization": "foo"}

        response = self.fetch(
            "/token", method="POST", body="", headers=headers)

        self.assertEqual(response.code, 415)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_post_not_json_content(self):
        headers = {"Authorization": "foo", "Content-Type": "application/json"}

        response = self.fetch(
            "/token", method="POST", body="", headers=headers)

        self.assertEqual(response.code, 422)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_post_wrong_json(self):
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps(dict(foo="foo", bar="bar"))

        response = self.fetch(
            "/token", method="POST", body=body, headers=headers)

        self.assertEqual(response.code, 400)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_post_new_no_email(self):
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps(dict(username="foo"))

        response = self.fetch(
            "/token", method="POST", headers=headers, body=body)

        self.assertEqual(response.code, 400)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_post_new_wrong_value(self):
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps(dict(email="bar", username="foo", get="1"))

        response = self.fetch(
            "/token", method="POST", headers=headers, body=body)

        self.assertEqual(response.code, 400)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_post_new_ip_restricted_wrong_0(self):
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps(dict(email="bar", username="foo", ip_restricted=1))

        response = self.fetch(
            "/token", method="POST", headers=headers, body=body)

        self.assertEqual(response.code, 400)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_post_new_ip_restricted_wrong_1(self):
        headers = {"Authorization": "foo", "Content-Type": "application/json"}

        body = json.dumps(dict(email="bar", username="foo", ip_address="127"))

        response = self.fetch(
            "/token", method="POST", headers=headers, body=body)

        self.assertEqual(response.code, 400)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_post_new_ip_restricted_wrong_2(self):
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps(
            dict(
                email="bar",
                username="foo", ip_restricted=0, ip_address="127")
        )

        response = self.fetch(
            "/token", method="POST", headers=headers, body=body)

        self.assertEqual(response.code, 400)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_post_new_expires_wrong(self):
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps(
            dict(email="bar", expires_on="2014"))

        response = self.fetch(
            "/token", method="POST", headers=headers, body=body)

        self.assertEqual(response.code, 400)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_post_new_correct(self):
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps(
            dict(
                email="bar", username="foo", expires_on="2014-07-01",
                admin=1, superuser=1, get=1, delete=1, post=1
            )
        )

        response = self.fetch(
            "/token", method="POST", headers=headers, body=body)

        self.assertEqual(response.code, 201)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)
        self.assertIsNotNone(response.headers["Location"])

    def test_post_with_id(self):
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps(dict(admin=1))

        response = self.fetch(
            "/token/token", method="POST", headers=headers, body=body)

        self.assertEqual(response.code, 400)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_put_without_token(self):
        body = json.dumps(dict(email="foo"))

        response = self.fetch("/token", method="PUT", body=body)

        self.assertEqual(response.code, 403)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_put_wrong_content_type(self):
        headers = {"Authorization": "foo"}

        response = self.fetch(
            "/token/token", method="PUT", body="", headers=headers)

        self.assertEqual(response.code, 415)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_put_not_json_content(self):
        headers = {"Authorization": "foo", "Content-Type": "application/json"}

        response = self.fetch(
            "/token/token", method="PUT", body="", headers=headers)

        self.assertEqual(response.code, 422)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_put_wrong_json(self):
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps(dict(foo="foo", bar="bar"))

        response = self.fetch(
            "/token/token", method="PUT", body=body, headers=headers)

        self.assertEqual(response.code, 400)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    @mock.patch("bson.objectid.ObjectId")
    def test_put_update_no_token(self, mock_id):
        mock_id.return_value = "token"
        headers = {"Authorization": "foo", "Content-Type": "application/json"}

        body = json.dumps(dict(admin=1))

        response = self.fetch(
            "/token/token", method="PUT", headers=headers, body=body)

        self.assertEqual(response.code, 404)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_put_no_id(self):
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps(dict(admin=1))

        response = self.fetch(
            "/token", method="PUT", headers=headers, body=body)

        self.assertEqual(response.code, 400)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    @mock.patch("bson.objectid.ObjectId")
    @mock.patch("handlers.token.TokenHandler.collection")
    def test_put_update_with_token(self, mock_collection, mock_id):
        mock_id.return_value = "token"
        mock_collection.find_one = mock.MagicMock()
        mock_collection.find_one.return_value = dict(
            _id="token", token="token")
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps(
            dict(admin=1, expired=1, lab=1, test_lab=1, upload=1))

        response = self.fetch(
            "/token/token", method="PUT", headers=headers, body=body)

        self.assertEqual(response.code, 200)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_put_update_wrong_id(self):
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps(
            dict(admin=1, expired=1, lab=1, test_lab=1, upload=1))

        response = self.fetch(
            "/token/token", method="PUT", headers=headers, body=body)

        self.assertEqual(response.code, 400)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    @mock.patch("bson.objectid.ObjectId")
    @mock.patch("handlers.token.TokenHandler.collection")
    def test_put_update_wrong_content_0(self, mock_collection, mock_id):
        mock_id.return_value = "token"
        mock_collection.find_one = mock.MagicMock()
        mock_collection.find_one.return_value = dict(token="token")
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps(dict(admin="bar"))

        response = self.fetch(
            "/token/token", method="PUT", headers=headers, body=body)

        self.assertEqual(response.code, 400)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    @mock.patch("bson.objectid.ObjectId")
    @mock.patch("handlers.token.TokenHandler.collection")
    def test_put_update_wrong_content_1(self, mock_collection, mock_id):
        mock_id.return_value = "token"
        mock_collection.find_one = mock.MagicMock()
        mock_collection.find_one.return_value = dict(
            token="token", email="email", properties=[0 for _ in range(0, 16)]
        )
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps(dict(ip_address="127"))

        response = self.fetch(
            "/token/token", method="PUT", headers=headers, body=body)

        self.assertEqual(response.code, 400)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    @mock.patch("bson.objectid.ObjectId")
    @mock.patch("handlers.token.TokenHandler.collection")
    def test_put_update_wrong_content_2(self, mock_collection, mock_id):
        mock_id.return_value = "token"
        mock_collection.find_one = mock.MagicMock()
        mock_collection.find_one.return_value = dict(
            token="token", email="email", properties=[0 for _ in range(0, 16)]
        )
        headers = {"Authorization": "foo", "Content-Type": "application/json"}
        body = json.dumps(dict(ip_restricted=1))

        response = self.fetch(
            "/token/token", method="PUT", headers=headers, body=body)

        self.assertEqual(response.code, 400)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    @mock.patch("bson.objectid.ObjectId")
    @mock.patch("handlers.token.TokenHandler.collection")
    def test_put_update_ip_restricted(self, mock_collection, mock_id):
        mock_id.return_value = "token"
        mock_collection.find_one = mock.MagicMock()
        mock_collection.find_one.return_value = dict(
            _id="token", token="token", email="email",
            properties=[0 for _ in range(0, 16)]
        )
        headers = {"Authorization": "foo", "Content-Type": "application/json"}

        body = json.dumps(dict(email="foo", ip_restricted=1, ip_address="127"))

        response = self.fetch(
            "/token/token", method="PUT", headers=headers, body=body)

        self.assertEqual(response.code, 200)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    def test_delete_no_token(self):
        response = self.fetch("/token/token", method="DELETE")
        self.assertEqual(response.code, 403)

    @mock.patch("bson.objectid.ObjectId")
    def test_delete_with_token_no_document(self, mock_id):
        mock_id.return_value = "token"
        headers = {"Authorization": "foo"}

        response = self.fetch(
            "/token/token", method="DELETE", headers=headers)

        self.assertEqual(response.code, 404)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    @mock.patch("bson.objectid.ObjectId")
    def test_delete_with_token_with_document(self, mock_id):
        mock_id.return_value = "token"

        self.database["api-token"].insert_one(
            dict(_id="token", token="token", email="email"))

        headers = {"Authorization": "foo"}

        response = self.fetch(
            "/token/token", method="DELETE", headers=headers)

        self.assertEqual(response.code, 200)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

        response = self.fetch(
            "/token/token", method="GET", headers=headers)
        self.assertEqual(response.code, 404)

    def test_delete_wrong_id_value(self):
        self.database["api-token"].insert_one(
            dict(_id="token", token="token", email="email"))

        headers = {"Authorization": "foo"}

        response = self.fetch(
            "/token/token", method="DELETE", headers=headers)

        self.assertEqual(response.code, 400)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)

    @mock.patch("utils.db.delete")
    @mock.patch("utils.db.find_one2")
    @mock.patch("bson.objectid.ObjectId")
    def test_delete_with_error(self, mock_id, mock_find, mock_delete):
        mock_id.return_value = "token"
        mock_find.return_value = {"_id": "token"}
        mock_delete.return_value = 500
        headers = {"Authorization": "foo"}

        response = self.fetch(
            "/token/token", method="DELETE", headers=headers)

        self.assertEqual(response.code, 500)
        self.assertEqual(
            response.headers["Content-Type"], self.content_type)
