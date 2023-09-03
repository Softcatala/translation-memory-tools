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
from builder.jsonbackend import ConversorSetupDTO
from polib import pofile
import unittest
from os import path, remove


class ConvertFilesTest(unittest.TestCase):
    def _get_po_entries(self, directory):
        entries = 0
        findFiles = FindFiles()
        for filename in findFiles.find_recursive(directory, "*.po"):
            po_file = pofile(filename)
            entries += len(po_file.translated_entries())

        return po_file, entries

    def _clean_pos(self, directory):
        findFiles = FindFiles()
        for filename in findFiles.find_recursive(directory, "*.po"):
            remove(filename)

    def test_convert_json_files_to_po(self):
        json_dir = path.dirname(path.realpath(__file__))
        json_dir += "/data/conversions/json/"
        convert = ConvertFiles(json_dir, None)
        convert.convert()

        po_file, entries = self._get_po_entries(json_dir)
        self._clean_pos(json_dir)

        self.assertEquals(entries, 781)
        self.assertEquals("Watch Movies and TV Shows instantly", po_file[3].msgid)
        self.assertEquals(
            "Mireu pel·lícules i sèries instantàniament", po_file[3].msgstr
        )

    def test_convert_yml_files_to_po(self):
        yml_dir = path.dirname(path.realpath(__file__))
        yml_dir += "/data/conversions/yml/"
        convert = ConvertFiles(yml_dir, None)
        convert.convert()

        po_file, entries = self._get_po_entries(yml_dir)
        self._clean_pos(yml_dir)

        self.assertEquals(entries, 3)
        self.assertEquals(
            "Enable imgur api for uploading, don't host files locally", po_file[0].msgid
        )
        self.assertEquals(
            "Habilita l'API d'imgur per pujades, no allotgis els arxius localment",
            po_file[0].msgstr,
        )

    def test_convert_csv_files_to_po(self):
        csv_dir = path.dirname(path.realpath(__file__))
        csv_dir += "/data/conversions/csv/"
        convert = ConvertFiles(csv_dir, None)
        convert.convert()

        po_file, entries = self._get_po_entries(csv_dir)
        self._clean_pos(csv_dir)

        self.assertEquals(entries, 4)
        self.assertEquals("Period Name", po_file[0].msgid)
        self.assertEquals("Nom del període", po_file[0].msgstr)

    def test_convert_ini_files_to_po(self):
        ini_dir = path.dirname(path.realpath(__file__))
        ini_dir += "/data/conversions/ini/"
        convert = ConvertFiles(ini_dir, None)
        convert.convert()

        po_file, entries = self._get_po_entries(ini_dir)
        self._clean_pos(ini_dir)

        self.assertEquals(entries, 15)
        self.assertEquals("Load More", po_file[10].msgid)
        self.assertEquals("Carregar més", po_file[10].msgstr)

    def test_convert_android_files_to_po(self):
        android_dir = path.dirname(path.realpath(__file__))
        android_dir += "/data/conversions/android/"
        convert = ConvertFiles(android_dir, None)
        convert.convert()

        po_file, entries = self._get_po_entries(android_dir)
        self._clean_pos(android_dir)

        self.assertEquals(entries, 392)
        self.assertEquals("Name is too long", po_file[14].msgid)
        self.assertEquals("El nom és massa llarg", po_file[14].msgstr)

    def test_convert_xliff_file_to_po(self):
        xliff_dir = path.dirname(path.realpath(__file__))
        xliff_dir += "/data/conversions/xliff"
        convert = ConvertFiles(xliff_dir, None)
        convert.convert()

        po_file, entries = self._get_po_entries(xliff_dir)
        self._clean_pos(xliff_dir)

        self.assertEquals(entries, 1)
        self.assertEquals("User Actions Log", po_file[0].msgid)
        self.assertEquals("Acció", po_file[1].msgstr)

    def test_convert_apple_files_to_po(self):
        apple_dir = path.dirname(path.realpath(__file__))
        apple_dir += "/data/conversions/apple/"
        convert = ConvertFiles(apple_dir, None)
        convert.convert()

        po_file, entries = self._get_po_entries(apple_dir)
        self._clean_pos(apple_dir)

        self.assertEquals(entries, 3)
        self.assertEquals("%1$@|New message", po_file[1].msgid)
        self.assertEquals("%1$@|Missatge nou", po_file[1].msgstr)

    def test_add_conversor_setup_to_cmd(self):
        CMD = "prop2po -t template.txt -i in.txt -o out.txt"
        COMMAND = " --encoding utf-16"

        conversor_setup = ConversorSetupDTO()
        conversor_setup.type = "properties"
        conversor_setup.verb = "add"
        conversor_setup.command = COMMAND

        convert = ConvertFiles(None, conversor_setup)
        r = convert._add_conversor_setup_to_cmd(cmd=CMD, conversor_id="properties")
        self.assertEquals(
            "prop2po -t template.txt -i in.txt -o out.txt --encoding utf-16", r
        )

    def test_add_conversor_setup_to_cmd_negative(self):
        CMD = "prop2po -t template.txt -i in.txt -o out.txt"
        COMMAND = " --encoding utf-16"

        conversor_setup = ConversorSetupDTO()
        conversor_setup.type = "properties"
        conversor_setup.verb = "add"
        conversor_setup.command = COMMAND

        convert = ConvertFiles(None, conversor_setup)
        r = convert._add_conversor_setup_to_cmd(cmd=CMD, conversor_id="ts")
        self.assertEquals("prop2po -t template.txt -i in.txt -o out.txt", r)

    def test_convert_strings_files_to_po(self):
        strings_dir = path.dirname(path.realpath(__file__))
        strings_dir += "/data/conversions/strings/"
        convert = ConvertFiles(strings_dir, None)
        convert.convert()

        po_file, entries = self._get_po_entries(strings_dir)
        self._clean_pos(strings_dir)

        self.assertEquals(entries, 6)
        self.assertEquals("Failed to verify the signature.", po_file[0].msgid)
        self.assertEquals("No s'ha pogut verificar la signatura.", po_file[0].msgstr)

    def test_convert_php_files_to_po(self):
        strings_dir = path.dirname(path.realpath(__file__))
        strings_dir += "/data/conversions/php/"
        convert = ConvertFiles(strings_dir, None)
        convert.convert()

        po_file, entries = self._get_po_entries(strings_dir)
        self._clean_pos(strings_dir)

        self.assertEquals(entries, 7)
        self.assertEquals("Add condition", po_file[0].msgid)
        self.assertEquals("Afegeix una condició", po_file[0].msgstr)


if __name__ == "__main__":
    unittest.main()
