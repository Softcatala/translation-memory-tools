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
        f = open(tmpfile.name, 'w')
        f.write(self.minipo)
        f.close()

        pofile = POFile(tmpfile.name)
        pofile.add_comment_to_all_entries(u'Comment test')

        input_po = polib.pofile(tmpfile.name)

        for entry in input_po:
            assert entry.tcomment == u'Comment test\nPlease remember to do something'

    def test_calculate_localized_string_checksum(self):
        pofile = POFile(self.minipo)
        checksum = hashlib.new('sha1')
        pofile.calculate_localized_string_checksum(checksum)
        self.assertEquals(u'edf879d0199103cc09cc464deebdfd3e98613e4b',
                    checksum.hexdigest())


if __name__ == '__main__':
    unittest.main()
