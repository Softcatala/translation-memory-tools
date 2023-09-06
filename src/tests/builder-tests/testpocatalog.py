# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import os
import tempfile
import unittest
import shutil
from builder.pocatalog import POCatalog
from polib import pofile


class POCatalogTest(unittest.TestCase):
    def test_pocatalog_onefile(self):
        catalog_dir = os.path.dirname(os.path.realpath(__file__))
        catalog_dir += "/data/catalog/"

        entries = None
        with tempfile.NamedTemporaryFile() as tmp:
            catalog_po = tmp.name
            catalog = POCatalog(catalog_po)
            catalog.add_pofile(os.path.join(catalog_dir, "ca1.po"))
            po_file = pofile(catalog_po)
            entries = po_file.translated_entries()

        self.assertEqual(1, len(entries))
        self.assertEqual("Clock rotation", po_file[0].msgid)
        self.assertEqual("Rotació del rellotge", po_file[0].msgstr)

    def test_pocatalog_twofiles(self):
        catalog_dir = os.path.dirname(os.path.realpath(__file__))
        catalog_dir += "/data/catalog/"

        entries = None
        with tempfile.NamedTemporaryFile() as tmp:
            catalog_po = tmp.name
            catalog = POCatalog(catalog_po)
            catalog.add_pofile(os.path.join(catalog_dir, "ca1.po"))
            catalog.add_pofile(os.path.join(catalog_dir, "ca2.po"))
            po_file = pofile(catalog_po)
            entries = po_file.translated_entries()

        self.assertEqual(3, len(entries))
        self.assertEqual("Clock rotation", po_file[0].msgid)
        self.assertEqual("Rotació del rellotge", po_file[0].msgstr)

    def test_pocatalog_cleanup(self):
        catalog_dir = os.path.dirname(os.path.realpath(__file__))
        catalog_dir += "/data/catalog/"

        entries = None
        with tempfile.NamedTemporaryFile() as tmp:
            catalog_po = tmp.name
            shutil.copyfile(os.path.join(catalog_dir, "ca1.po"), catalog_po)
            catalog = POCatalog(catalog_po)
            catalog.cleanup()
            po_file = pofile(catalog_po)
            entries = po_file.translated_entries()
            fuzzy = po_file.fuzzy_entries()

        self.assertEqual(1, len(entries))
        self.assertEqual(0, len(fuzzy))
        self.assertEqual("Clock rotation", po_file[0].msgid)
        self.assertEqual("Rotació del rellotge", po_file[0].msgstr)


if __name__ == "__main__":
    unittest.main()
