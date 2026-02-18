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
import tempfile
import shutil


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

        self.assertEqual(entries, 781)
        self.assertEqual("Watch Movies and TV Shows instantly", po_file[3].msgid)
        self.assertEqual(
            "Mireu pel·lícules i sèries instantàniament", po_file[3].msgstr
        )

    def test_convert_json_files_to_po_locations(self):
        json_dir = path.dirname(path.realpath(__file__))
        json_dir += "/data/conversions/json/"

        src_en = path.join(json_dir, "translations/popcorn-time-app.en-json/en.json")
        tgt_ca = path.join(json_dir, "translations/popcorn-time-app.en-json/ca.json")

        srcs = [
            "en.json",
            "en-US.json",
            "en.i18n.json",
            "main.json",
            "strings.i18n.json",
        ]
        tgts = [
            "ca.json",
            "ca.json",
            "ca.i18n.json",
            "main-ca.json",
            "strings_ca.i18n.json",
        ]

        for idx in range(len(srcs)):
            with tempfile.TemporaryDirectory() as temp_dir:
                src = path.join(temp_dir, srcs[idx])
                shutil.copyfile(src_en, src)

                tgt = path.join(temp_dir, tgts[idx])
                shutil.copyfile(tgt_ca, tgt)

                convert = ConvertFiles(temp_dir, None)
                convert.convert()

                po_file, entries = self._get_po_entries(temp_dir)
                self.assertEqual(entries, 477)
                self.assertEqual(
                    "Initializing PopcornTime. Please Wait...", po_file[3].msgid
                )
                self.assertEqual(
                    "S'està inicialitzant PopcornTime, espereu...", po_file[3].msgstr
                )

    def test_convert_yml_files_to_po(self):
        yml_dir = path.dirname(path.realpath(__file__))
        yml_dir += "/data/conversions/yml/"
        convert = ConvertFiles(yml_dir, None)
        convert.convert()

        po_file, entries = self._get_po_entries(yml_dir)
        self._clean_pos(yml_dir)

        self.assertEqual(entries, 3)
        self.assertEqual(
            "Enable imgur api for uploading, don't host files locally", po_file[0].msgid
        )
        self.assertEqual(
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

        self.assertEqual(entries, 4)
        self.assertEqual("Period Name", po_file[0].msgid)
        self.assertEqual("Nom del període", po_file[0].msgstr)

    def test_convert_ini_files_to_po(self):
        ini_dir = path.dirname(path.realpath(__file__))
        ini_dir += "/data/conversions/ini/"
        convert = ConvertFiles(ini_dir, None)
        convert.convert()

        po_file, entries = self._get_po_entries(ini_dir)
        self._clean_pos(ini_dir)

        self.assertEqual(entries, 15)
        self.assertEqual("Load More", po_file[10].msgid)
        self.assertEqual("Carregar més", po_file[10].msgstr)

    def test_convert_android_files_to_po(self):
        android_dir = path.dirname(path.realpath(__file__))
        android_dir += "/data/conversions/android/"
        convert = ConvertFiles(android_dir, None)
        convert.convert()

        po_file, entries = self._get_po_entries(android_dir)
        self._clean_pos(android_dir)

        self.assertEqual(entries, 392)
        self.assertEqual("Name is too long", po_file[14].msgid)
        self.assertEqual("El nom és massa llarg", po_file[14].msgstr)

    def test_convert_xliff_file_to_po(self):
        xliff_dir = path.dirname(path.realpath(__file__))
        xliff_dir += "/data/conversions/xliff"
        convert = ConvertFiles(xliff_dir, None)
        convert.convert()

        po_file, entries = self._get_po_entries(xliff_dir)
        self._clean_pos(xliff_dir)

        self.assertEqual(entries, 1)
        self.assertEqual("User Actions Log", po_file[0].msgid)
        self.assertEqual("Acció", po_file[1].msgstr)

    def test_convert_apple_files_to_po(self):
        apple_dir = path.dirname(path.realpath(__file__))
        apple_dir += "/data/conversions/apple/"
        convert = ConvertFiles(apple_dir, None)
        convert.convert()

        po_file, entries = self._get_po_entries(apple_dir)
        self._clean_pos(apple_dir)

        self.assertEqual(entries, 3)
        self.assertEqual("%1$@|New message", po_file[1].msgid)
        self.assertEqual("%1$@|Missatge nou", po_file[1].msgstr)

    def test_add_conversor_setup_to_cmd(self):
        CMD = "prop2po -t template.txt -i in.txt -o out.txt"
        COMMAND = " --encoding utf-16"

        conversor_setup = ConversorSetupDTO()
        conversor_setup.type = "properties"
        conversor_setup.verb = "add"
        conversor_setup.command = COMMAND

        convert = ConvertFiles(None, conversor_setup)
        r = convert._add_conversor_setup_to_cmd(cmd=CMD, conversor_id="properties")
        self.assertEqual(
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
        self.assertEqual("prop2po -t template.txt -i in.txt -o out.txt", r)

    def test_convert_strings_files_to_po(self):
        strings_dir = path.dirname(path.realpath(__file__))
        strings_dir += "/data/conversions/strings/"
        convert = ConvertFiles(strings_dir, None)
        convert.convert()

        po_file, entries = self._get_po_entries(strings_dir)
        self._clean_pos(strings_dir)

        self.assertEqual(entries, 6)
        self.assertEqual("Failed to verify the signature.", po_file[0].msgid)
        self.assertEqual("No s'ha pogut verificar la signatura.", po_file[0].msgstr)

    def test_convert_php_files_to_po(self):
        strings_dir = path.dirname(path.realpath(__file__))
        strings_dir += "/data/conversions/php/"
        convert = ConvertFiles(strings_dir, None)
        convert.convert()

        po_file, entries = self._get_po_entries(strings_dir)
        self._clean_pos(strings_dir)

        self.assertEqual(entries, 7)
        self.assertEqual("Add condition", po_file[0].msgid)
        self.assertEqual("Afegeix una condició", po_file[0].msgstr)

    def test_convert_ts_files_to_po(self):
        ts_dir = path.dirname(path.realpath(__file__))
        ts_dir += "/data/conversions/ts/"
        convert = ConvertFiles(ts_dir, None)
        convert.convert()

        po_file, entries = self._get_po_entries(ts_dir)
        self._clean_pos(ts_dir)

        self.assertEqual(entries, 2)
        self.assertEqual("Hello World", po_file[0].msgid)
        self.assertEqual("Hola Món", po_file[0].msgstr)

    def test_is_qt_ts_file(self):
        ts_dir = path.dirname(path.realpath(__file__))
        ts_dir += "/data/conversions/ts/"
        convert = ConvertFiles(ts_dir, None)

        self.assertTrue(convert._is_qt_ts_file(ts_dir + "qt-translation.ts"))
        self.assertFalse(convert._is_qt_ts_file(ts_dir + "typescript-source.ts"))


if __name__ == "__main__":
    unittest.main()
