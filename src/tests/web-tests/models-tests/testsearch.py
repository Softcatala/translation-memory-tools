# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import json

from web.indexcreator import IndexCreator
from web.models.search import Search


class TestSearch(unittest.TestCase):
    PROJECT_GNOME = "gnome"
    PROJECT_ABI = "abiword"
    PROJECT_MICROSOFT = "Microsoft Terminology"
    SC = True
    NO_SC = False

    data_set = [
        "Nox Documents Found",
        "No s'han trobat",
        PROJECT_GNOME,
        SC,
        "No Documents Found Today",
        "No s'han trobat documents avui",
        PROJECT_GNOME,
        SC,
        "No Documents Found late Yesterday",
        "No s'han trobat documents ahir",
        PROJECT_GNOME,
        SC,
        "Many documents found Yesterday",
        "S'han trobat molts errors ahir",
        PROJECT_ABI,
        SC,
        "Many documents found Yesterday Microsoft",
        "S'han trobat molts errors ahir Microsoft",
        PROJECT_MICROSOFT,
        NO_SC,
    ]

    FIELDS = 4

    def _create_index(self):
        """Creates an index in RAM with the entries from data_set array"""
        self.index = IndexCreator("")
        index = self.index.create(True)

        for idx in range(0, len(self.data_set), self.FIELDS):
            self.index.write_entry(
                source=self.data_set[idx + 0],
                target=self.data_set[idx + 1],
                comment="",
                context="",
                project_name=self.data_set[idx + 2],
                project_id=self.data_set[idx + 2] + "_id",
                softcatala=self.data_set[idx + 3],
            )

        self.index.writer.commit()
        return index

    def test_query_simple_query_source(self):
        ix = self._create_index()
        search = Search("Today", None, "gnome_id")
        search.search(ix)
        results = search.get_results()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["source"], "No Documents Found Today")

    def test_query_simple_query_source_with_two_projects(self):
        ix = self._create_index()
        search = Search("Yesterday", None, "gnome_id,abiword_id")
        search.search(ix)
        results = search.get_results()

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["source"], "Many documents found Yesterday")
        self.assertEqual(results[1]["source"], "No Documents Found late Yesterday")

    def test_query_simple_query_source_with_three_projects_with_spaces(self):
        ix = self._create_index()
        search = Search(
            "Yesterday", None, "gnome_id,abiword_id,Microsoft Terminology_id"
        )
        search.search(ix)
        results = search.get_results()

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["source"], "Many documents found Yesterday")
        self.assertEqual(results[1]["source"], "No Documents Found late Yesterday")
        self.assertEqual(
            results[2]["source"], "Many documents found Yesterday Microsoft"
        )

    def test_query_simple_query_source_with_single_project_with_spaces(self):
        ix = self._create_index()
        search = Search("Yesterday", None, "Microsoft Terminology_id")
        search.search(ix)
        results = search.get_results()

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["source"], "Many documents found Yesterday Microsoft"
        )

    def test_query_simple_query_source_with_no_project(self):
        ix = self._create_index()
        search = Search("Yesterday", None, "")
        search.search(ix)
        results = search.get_results()

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["source"], "Many documents found Yesterday")
        self.assertEqual(results[1]["source"], "No Documents Found late Yesterday")
        self.assertEqual(
            results[2]["source"], "Many documents found Yesterday Microsoft"
        )

    def test_query_simple_with_or_query_source(self):
        ix = self._create_index()
        search = Search("Today OR Yesterday", None, "gnome_id")
        search.search(ix)
        results = search.get_results()

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["source"], "No Documents Found Today")
        self.assertEqual(results[1]["source"], "No Documents Found late Yesterday")

    def test_query_simple_with_not_query_source(self):
        ix = self._create_index()
        search = Search("Documents NOT Yesterday", None, "gnome_id")
        search.search(ix)
        results = search.get_results()

        self.assertEqual(len(results), 2)
        for i in range(0, len(results)):
            self.assertFalse("Yesterday" in results[i]["source"])

    def test_query_simple_with_and_query_source(self):
        ix = self._create_index()
        search = Search("Documents AND late", None, "gnome_id")
        search.search(ix)
        results = search.get_results()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["source"], "No Documents Found late Yesterday")

    def test_query_source_target(self):
        ix = self._create_index()
        search = Search("Documents", "Ahir", "gnome_id")
        search.search(ix)
        results = search.get_results()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["source"], "No Documents Found late Yesterday")

    def test_query_source_OR_target(self):
        ix = self._create_index()
        search = Search("Today OR No", "trobat", "gnome_id")
        search.search(ix)
        results = search.get_results()

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["source"], "No Documents Found Today")
        self.assertEqual(results[1]["source"], "No Documents Found late Yesterday")

    def test_get_json(self):
        ix = self._create_index()
        search = Search("Today OR No", "trobat", "gnome_id")
        search.search(ix)
        results = search.get_json()

        json_array = json.loads(results)
        self.assertEqual(len(json_array), 2)
        self.assertEqual(json_array[0]["source"], "No Documents Found Today")
        self.assertEqual(json_array[1]["source"], "No Documents Found late Yesterday")


if __name__ == "__main__":
    unittest.main()
