# -*- coding: utf-8 -*-
#
# Copyright (c) 2024 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from builder.weblatefileset import WeblateFileSet
import unittest
from unittest.mock import patch


class TestWeblateFileSet(unittest.TestCase):
    @patch("builder.weblatefileset.WeblateFileSet._api_json_call")
    def test_get_catalan_language_ca_es(self, mock_api_json_call):
        mock_api_json_call.return_value = [
            {"code": "en", "translated": 10},
            {"code": "ca_es", "translated": 7},
        ]

        weblate = WeblateFileSet(
            "project_test", "test_id", "name", "no_url", "filename.po"
        )
        result = weblate._get_catalan_language("test_url")
        self.assertEqual("ca_es", result)

    @patch("builder.weblatefileset.WeblateFileSet._api_json_call")
    def test_get_catalan_language_ca(self, mock_api_json_call):
        mock_api_json_call.return_value = [
            {"code": "en", "translated": 10},
            {"code": "ca", "translated": 1},
        ]
        weblate = WeblateFileSet(
            "project_test", "test_id", "name", "no_url", "filename.po"
        )
        result = weblate._get_catalan_language("test_url")
        self.assertEqual("ca", result)

    @patch("builder.weblatefileset.WeblateFileSet._api_json_call")
    def test_get_catalan_language_ca_no_translated(self, mock_api_json_call):
        mock_api_json_call.return_value = [
            {"code": "en", "translated": 10},
            {"code": "ca", "translated": 0},
        ]
        weblate = WeblateFileSet(
            "project_test", "test_id", "name", "no_url", "filename.po"
        )
        result = weblate._get_catalan_language("test_url")
        self.assertEqual(None, result)

    @patch("builder.weblatefileset.WeblateFileSet._api_json_call")
    def test_get_catalan_language_ca_nolang(self, mock_api_json_call):
        mock_api_json_call.return_value = [
            {"code": "en", "translated": 10},
        ]
        weblate = WeblateFileSet(
            "project_test", "test_id", "name", "no_url", "filename.po"
        )
        result = weblate._get_catalan_language("test_url")
        self.assertEqual(None, result)


if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()
