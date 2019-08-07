# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from builder.converttmx import ConvertTmx
import unittest
import polib
import tempfile
from os import path


class TestConvertTmx(unittest.TestCase):

    def _get_files(self, filename):
        tmx_file = path.dirname(path.realpath(__file__))
        tmx_file += '/data/conversions/tmx/{0}'.format(filename)

        tmpfile = tempfile.NamedTemporaryFile()
        po_filename = tmpfile.name + ".po"

        return tmx_file, po_filename

    def test_convertion(self):
        tmx_file, po_filename = self._get_files('test.tmx')
        convertTmx = ConvertTmx(tmx_file, po_filename)
        convertTmx.convert()

        entries = polib.pofile(po_filename)

        self.assertEquals(len(entries), 2)
        self.assertEquals(entries[0].msgid, "Modern visual refresh")
        self.assertEquals(entries[0].msgstr, "Una renovació visual moderna")
        self.assertEquals(entries[0].tcomment, "id: appstores:fx_androidwhatsnewandroid_57lang:a-clean-modern-visual-refresh");

        self.assertEquals(entries[1].msgid, "As You Like It")
        self.assertEquals(entries[1].msgstr, "Com vulgueu")
        self.assertEquals(entries[1].tcomment, '')

    def test_convertion_omegat(self):
        tmx_file, po_filename = self._get_files('omegat.tmx')
        convertTmx = ConvertTmx(tmx_file, po_filename)
        convertTmx.convert()

        entries = polib.pofile(po_filename)

        self.assertEquals(len(entries), 1)
        self.assertEquals(entries[0].msgid, '"Aligner" aligner utility')
        self.assertEquals(entries[0].msgstr, 'Alineador de textos "Aligner"')
        self.assertEquals(entries[0].tcomment, '');

if __name__ == '__main__':
    unittest.main()
