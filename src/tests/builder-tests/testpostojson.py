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

import tempfile
import unittest
import json
import polib
from whoosh.writing import *
import sys

sys.path.append("web/")

from builder.postojson import POsToJson


class TestIndexCreator(unittest.TestCase):
    minipo = r"""#
msgid ""
msgstr ""
"Project-Id-Version: program 2.1-branch\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2006-01-09 07:15+0100\n"
"PO-Revision-Date: 2004-03-30 17:02+0200\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

# Please remember to do something
#: ../dir/file.xml.in.h:1 ../dir/file2.xml.in.h:4
msgctxt "Context"
msgid "Power off the selected virtual machines"
msgstr "Apaga les màquines virtuals seleccionades"
"""

    minipo_plural = r"""#
msgid ""
msgstr ""
"Project-Id-Version: program 2.1-branch\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2006-01-09 07:15+0100\n"
"PO-Revision-Date: 2004-03-30 17:02+0200\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

# Please remember to do something
#: ../dir/file.xml.in.h:1 ../dir/file2.xml.in.h:4
msgctxt "Context"
msgid "Delete this photo from camera?"
msgid_plural "Delete these %d photos from camera?"
msgstr[0] "Voleu suprimir aquesta fotografia de la càmera?"
msgstr[1] "Voleu suprimir aquestes %d fotografies de la càmera?"
"""

    def _dump_po_to_file(self, filename):
        tmpfile = tempfile.NamedTemporaryFile()
        f = open(tmpfile.name, "w")
        f.write(filename)
        return tmpfile

    def test_process_project(self):
        tmpfile = self._dump_po_to_file(self.minipo)

        posToJson = POsToJson(".")
        posToJson._process_file(
            "test_project_id", "test_project", tmpfile.name, False, set()
        )
        posToJson.save_index()
        with open("index_data.json") as f:
            stored = json.load(f)

        self.assertEqual(stored[0]["s"], "Power off the selected virtual machines")
        self.assertEqual(stored[0]["t"], "Apaga les màquines virtuals seleccionades")
        self.assertEqual(stored[0]["c"], "Please remember to do something\r\n")
        self.assertEqual(stored[0]["x"], "Context")
        self.assertEqual(stored[0]["pn"], "test_project")
        self.assertEqual(stored[0]["pi"], "test_project_id")
        self.assertEqual(stored[0]["sc"], False)

    def test_process_project_plural(self):
        tmpfile = self._dump_po_to_file(self.minipo_plural)

        posToJson = POsToJson(".")
        posToJson._process_file(
            "test_project_id", "test_project", tmpfile.name, False, set()
        )

        posToJson.save_index()
        with open("index_data.json") as f:
            stored = json.load(f)

        self.assertEqual(stored[0]["s"], "Delete this photo from camera?")
        self.assertEqual(
            stored[0]["t"], "Voleu suprimir aquesta fotografia de la càmera?"
        )

        self.assertEqual(stored[1]["s"], "Delete these %d photos from camera?")
        self.assertEqual(
            stored[1]["t"], "Voleu suprimir aquestes %d fotografies de la càmera?"
        )

    def test_get_comment_both(self):
        posToJson = POsToJson(".")
        entry = polib.POEntry()
        entry.comment = "comment"
        entry.tcomment = "tcomment"
        comment = posToJson._get_comment(entry)
        self.assertEqual(comment, "tcomment\r\ncomment")


if __name__ == "__main__":
    unittest.main()
