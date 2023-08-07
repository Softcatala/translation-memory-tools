# -*- coding: utf-8 -*-
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

from builder.pofile import POFile
import unittest
import polib
import tempfile
import hashlib


class TestPOFile(unittest.TestCase):
    minipo = r"""# Afrikaans translation of program ABC
#
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
msgctxt 'Context'
msgid 'Power off the selected virtual machines'
msgstr 'Apaga les màquines virtuals seleccionades'
"""

    def test_get_statistics(self):
        pofile = POFile(self.minipo)
        assert pofile.get_statistics() == 5

    def test_add_comment_to_all_entries(self):
        tmpfile = tempfile.NamedTemporaryFile()
        f = open(tmpfile.name, "w")
        f.write(self.minipo)
        f.close()

        pofile = POFile(tmpfile.name)
        pofile.add_comment_to_all_entries_and_remove_fuzzys("Comment test")

        input_po = polib.pofile(tmpfile.name)

        for entry in input_po:
            assert entry.tcomment == "Comment test\nPlease remember to do something"

    def test_calculate_localized_string_checksum(self):
        pofile = POFile(self.minipo)
        checksum = hashlib.new("sha1")
        pofile.calculate_localized_string_checksum(checksum)
        self.assertEquals(
            "edf879d0199103cc09cc464deebdfd3e98613e4b", checksum.hexdigest()
        )

    def _create_po_with_duplicated_strings(self, filename):
        pofile = polib.POFile()
        entry = polib.POEntry(msgid="File", msgstr="Fitxer")
        pofile.append(entry)
        pofile.append(entry)
        pofile.save(filename)

    def _create_po_with_untranslated_strings(self, filename):
        pofile = polib.POFile()
        entry = polib.POEntry(msgid="File", msgstr="File")
        pofile.append(entry)
        entry = polib.POEntry(msgid="Exit", msgstr="Surt")
        pofile.append(entry)
        pofile.save(filename)

    def _does_pofile_contains_duplicated_strings(self, filename):
        strs = []

        print(filename)
        po = polib.pofile(filename)
        for entry in po:
            _str = entry.msgid
            if entry.msgctxt is not None:
                _str += entry.msgid

            if _str in strs:
                return True
            strs.append(_str)

        return False

    def test_add_msgctxt_to_duplicates(self):
        tmpfile = tempfile.NamedTemporaryFile()
        filename = tmpfile.name + ".po"
        self._create_po_with_duplicated_strings(filename)

        poFile = POFile(filename)
        poFile.add_msgctxt_to_duplicates()

        rslt = self._does_pofile_contains_duplicated_strings(filename)
        self.assertEquals(False, rslt)

    def test_remove_untranslated_strings(self):
        tmpfile = tempfile.NamedTemporaryFile()
        filename = tmpfile.name + ".po"
        self._create_po_with_untranslated_strings(filename)

        poFile = POFile(filename)
        poFile._remove_untranslated_strings()

        po = polib.pofile(filename)
        self.assertEquals(1, len(po))

    def _create_po_with_html(self, filename):
        pofile = polib.POFile()
        entry = polib.POEntry()
        entry = polib.POEntry(msgid="use the &lt;li&gt; to begin each list item")
        pofile.append(entry)
        entry = polib.POEntry(msgid="Hi", msgstr="&quot;Hi&quot;")
        pofile.append(entry)
        pofile.save(filename)

    def test_unescape_html(self):
        tmpfile = tempfile.NamedTemporaryFile()
        filename = tmpfile.name + ".po"

        self._create_po_with_html(filename)
        poFile = POFile(filename)
        poFile._unescape_html()

        po = polib.pofile(filename)
        self.assertEquals("use the <li> to begin each list item", po[0].msgid)

        self.assertEquals('"Hi"', po[1].msgstr)


if __name__ == "__main__":
    unittest.main()
