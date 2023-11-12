# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Jordi Mas i Hernandez <jmas@softcatala.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import unittest
from whoosh.writing import *
import os
import sys

sys.path.append("web/")
from web.indexcreator import IndexCreator


class IndexWriterMock(IndexWriter):
    def __init__(self):
        self.store = []

    def add_document(self, **fields):
        d = dict()
        d.update(fields)
        self.store.append(d)


class TestIndexCreator(unittest.TestCase):
    def test_process_project(self):
        json_dir = os.path.dirname(os.path.realpath(__file__))
        json_file = os.path.join(json_dir, "data/index_data.json")

        index = IndexCreator(json_file)
        index.writer = IndexWriterMock()
        index.process_entries()
        stored = index.writer.store

        self.assertEqual(
            stored[0]["source"],
            " - Reserved. \n You cannot use this name. Choose Another \n",
        )
        self.assertEqual(
            stored[0]["target"],
            " - est\u00e0 reservat. \n No podeu utilitzar aquest nom. Escolliu-ne un altre \n",
        )
        self.assertEqual(stored[0]["context"], "context")
        self.assertEqual(
            stored[0]["comment"],
            "Source: /abiword-ca.po from project 'Abiword'\r\nDLG_Styles_ErrNotTitle2",
        )
        self.assertEqual(stored[0]["softcatala"], True)
        self.assertEqual(stored[0]["project"], "Abiword")
        self.assertEqual(2, len(stored), 5)


if __name__ == "__main__":
    unittest.main()
