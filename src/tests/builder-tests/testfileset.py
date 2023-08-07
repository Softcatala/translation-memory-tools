#
# Copyright (c) 2013 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from builder.fileset import FileSet
from builder.findfiles import FindFiles
import unittest
import shutil
import os


class TestFileSet(unittest.TestCase):
    def _get_fileset(self):
        return FileSet(
            "project none",
            "project id",
            "filsetname",
            "lp:~mailman-l10n-ca/mailman.po",
            "none.po",
        )

    def test_has_filename_filename(self):
        fileset = self._get_fileset()
        fileset.add_excluded("excluded.po")

        self.assertTrue(fileset._should_exclude_file("excluded.po"))
        self.assertTrue(fileset._should_exclude_file("Includesexcluded.po"))
        self.assertFalse(fileset._should_exclude_file("eXcluded.po"))

    def test_has_filename_filename_project(self):
        fileset_parent = self._get_fileset()
        fileset_parent.po_preprocessing = "po_processing"
        fileset_parent.conversor_setup = "conversor_setup"

        fileset = FileSet(
            "project none",
            "project id",
            "filsetname",
            "lp:~mailman-l10n-ca/mailman.po",
            "none.po",
            fileset_parent,
        )

        self.assertEquals(fileset.po_preprocessing, "po_processing")
        self.assertEquals(fileset.conversor_setup, "conversor_setup")

    def test_remove_non_translation_files_no_pattern(self):
        fileset = self._get_fileset()
        directory = os.path.dirname(os.path.realpath(__file__))
        directory += "/data/fileset/"
        shutil.copytree(directory, fileset.temp_dir)

        fileset._remove_non_translation_files()

        findFiles = FindFiles()
        files = findFiles.find_recursive(fileset.temp_dir, "*.po")
        self.assertEquals(2, len(files))

    def test_remove_non_translation_files_pattern(self):
        fileset = self._get_fileset()
        directory = os.path.dirname(os.path.realpath(__file__))
        directory += "/data/fileset/"
        shutil.copytree(directory, fileset.temp_dir)

        fileset.set_pattern(r".*?ca\.po")
        fileset._remove_non_translation_files()

        findFiles = FindFiles()
        files = findFiles.find_recursive(fileset.temp_dir, "*.po")
        self.assertEquals(1, len(files))


if __name__ == "__main__":
    unittest.main()
