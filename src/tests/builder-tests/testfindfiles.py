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

from builder.findfiles import FindFiles
import unittest
from os import path


class TestFindFiles(unittest.TestCase):

    def test_find_recursive(self):
        directory = path.dirname(path.realpath(__file__))
        directory += '/data/findfiles/'

        filenames = FindFiles().find_recursive(directory, "*")

        results = []
        for filename in filenames:
            results.append(filename[len(directory):])

        self.assertEqual(6, len(results))
        self.assertEqual("dir1/dir1-dir2/dir1-dir2-file1.txt", results[0])
        self.assertEqual("dir1/dir1-file1.txt", results[1])
        self.assertEqual("dir1/dir1-file2.txt", results[2])
        self.assertEqual("dir2/dir2-file1.txt", results[3])
        self.assertEqual("root-file1.txt", results[4])
        self.assertEqual("root-file2.txt", results[5])

    def test_find_recursive_filter(self):
        directory = path.dirname(path.realpath(__file__))
        directory += '/data/findfiles/'

        filenames = FindFiles().find_recursive(directory, "root*")

        self.assertEqual(2, len(filenames))

if __name__ == '__main__':
    unittest.main()
