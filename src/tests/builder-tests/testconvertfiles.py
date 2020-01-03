#
# Copyright (c) 2015, 2018 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from builder.findfiles import FindFiles
from builder.convertfiles import ConvertFiles
from polib import pofile

import unittest
from os import path, remove


class ConvertFilesTest(unittest.TestCase):

    def _get_po_entries(self, directory):
        entries = 0
        findFiles = FindFiles()
        for filename in findFiles.find(directory, '*.po'):
            poFile = pofile(filename)
            entries += len(poFile.translated_entries())

        return entries

    def _clean_pos(self, directory):
        findFiles = FindFiles()
        for filename in findFiles.find(directory, '*.po'):
            remove(filename)

    def test_convert_json_files_to_po(self):

        json_dir = path.dirname(path.realpath(__file__))
        json_dir += '/data/conversions/json/'
        convert = ConvertFiles(json_dir, None)
        convert.convert()

        entries = self._get_po_entries(json_dir)
        self._clean_pos(json_dir)
        self.assertEquals(entries, 781)

    def test_convert_yml_files_to_po(self):

        yml_dir = path.dirname(path.realpath(__file__))
        yml_dir += '/data/conversions/yml/'
        convert = ConvertFiles(yml_dir, None)
        convert.convert()

        entries = self._get_po_entries(yml_dir)
        self._clean_pos(yml_dir)
        self.assertEquals(entries, 3)

    def test_convert_csv_files_to_po(self):

        csv_dir = path.dirname(path.realpath(__file__))
        csv_dir += '/data/conversions/csv/'
        convert = ConvertFiles(csv_dir, None)
        convert.convert()

        entries = self._get_po_entries(csv_dir)
        self._clean_pos(csv_dir)
        self.assertEquals(entries, 4)

    def test_convert_ini_files_to_po(self):

        ini_dir = path.dirname(path.realpath(__file__))
        ini_dir += '/data/conversions/ini/'
        convert = ConvertFiles(ini_dir, None)
        convert.convert()

        entries = self._get_po_entries(ini_dir)
        self._clean_pos(ini_dir)
        self.assertEquals(entries, 15)


    def test_convert_android_files_to_po(self):

        android_dir = path.dirname(path.realpath(__file__))
        android_dir += '/data/conversions/android/'
        convert = ConvertFiles(android_dir, None)
        convert.convert()

        entries = self._get_po_entries(android_dir)
        self._clean_pos(android_dir)
        self.assertEquals(entries, 392)

if __name__ == '__main__':
    unittest.main()
