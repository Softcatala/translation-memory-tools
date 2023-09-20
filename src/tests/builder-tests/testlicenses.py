# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from builder.licenses import Licenses
import unittest
from os import path


class TestLicenses(unittest.TestCase):
    def _get_licenses_file(self):
        current_dir = path.dirname(path.realpath(__file__))
        return path.join(current_dir, "data/licenses/licenses.json")

    def test_get_licenses_ids(self):
        ids = Licenses(self._get_licenses_file()).get_licenses_ids()
        self.assertEqual(6, len(ids))
        self.assertIn("PSF-2.0", ids)

    def test_get_licenses_name_and_link(self):
        links = Licenses(self._get_licenses_file()).get_licenses_name_and_link()
        self.assertEqual(5, len(links))
        license = links["PSF-2.0"]

        self.assertIn("Python Software Foundation License 2.0", license["name"])
        self.assertIn("https://opensource.org/licenses/Python-2.0", license["link"])

    def test_are_compatible_licenses_ok(self):
        licences = Licenses()
        self.assertFalse(
            licences.are_compatible_licenses("GPL-3.0-only", "GPL-2.0-only")
        )

    def test_are_compatible_licenses_false(self):
        licences = Licenses()
        self.assertTrue(
            licences.are_compatible_licenses("GPL-3.0-only", '"Apache-2.0"')
        )


if __name__ == "__main__":
    unittest.main()
