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

import unittest

import models.bisect as mbisect
import utils.bisect.common as bcommon


class BisectUtilsTest(unittest.TestCase):

    def test_get_docs_until_pass_no_pass(self):
        doc_list = [
            {"status": "foo", "id": 1},
            {"status": "foo", "id": 2},
            {"status": "foo", "id": 3},
            {"status": "foo", "id": 4},
            {"status": "foo", "id": 5},
        ]

        retrieved_list = [doc for doc in bcommon.get_docs_until_pass(doc_list)]
        self.assertListEqual(doc_list, retrieved_list)

    def test_get_docs_until_pass_with_pass_last(self):
        doc_list = [
            {"status": "foo", "id": 1},
            {"status": "foo", "id": 2},
            {"status": "foo", "id": 3},
            {"status": "foo", "id": 4},
            {"status": "PASS", "id": 5},
        ]

        retrieved_list = [doc for doc in bcommon.get_docs_until_pass(doc_list)]
        self.assertListEqual(doc_list, retrieved_list)

    def test_get_docs_until_pass_with_pass(self):
        doc_list = [
            {"status": "foo", "id": 1},
            {"status": "foo", "id": 2},
            {"status": "PASS", "id": 3},
            {"status": "foo", "id": 4},
            {"status": "foo", "id": 5},
        ]

        retrieved_list = [doc for doc in bcommon.get_docs_until_pass(doc_list)]
        self.assertEqual(len(retrieved_list), 3)
        self.assertListEqual(doc_list[:3], retrieved_list)

    def test_update_doc_fields_list(self):
        bisect_doc = mbisect.BisectDocument()
        bisect_doc.id = "bar"
        fields = ["good_commit", "foo", "bar"]

        expected = {
            "_id": "bar",
            "good_commit": None
        }

        self.assertDictEqual(
            expected, bcommon.update_doc_fields(bisect_doc, fields))

    def test_update_doc_fields_dict(self):
        bisect_doc = mbisect.BisectDocument()
        bisect_doc.id = "bar"
        fields = {
            "bad_commit": True,
            "_id": False,
            "good_commit": False,
            "foo": False,
            "bar": True
        }

        expected = {
            "bad_commit": None
        }

        self.assertDictEqual(
            expected, bcommon.update_doc_fields(bisect_doc, fields))

    def test_update_doc_fields_no_fields(self):
        bisect_doc = mbisect.BisectDocument()
        bisect_doc.id = "bar"

        self.assertDictEqual(
            bisect_doc.to_dict(), bcommon.update_doc_fields(bisect_doc, None)
        )

    def test_update_doc_fields_no_fields_type(self):
        bisect_doc = mbisect.BisectDocument()
        bisect_doc.id = "bar"

        self.assertDictEqual(
            bisect_doc.to_dict(), bcommon.update_doc_fields(bisect_doc, "None")
        )
        self.assertDictEqual(
            bisect_doc.to_dict(),
            bcommon.update_doc_fields(bisect_doc, ("None", None))
        )
