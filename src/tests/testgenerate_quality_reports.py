# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from generate_quality_reports import GenerateQualityReports
import unittest
import polib
import tempfile


class TestPOFile(unittest.TestCase):

    def _create_po_file(self, filename, entries):
        pofile = polib.POFile()

        for entry in entries:
            pofile.append(entry)

        pofile.save(filename)

    def _read_text_file(self, text_file):
        with open(text_file) as fp:
            return fp.readlines()

    def _generate_po_and_extract(self, entries):
        filename = tempfile.NamedTemporaryFile().name
        text_file = tempfile.NamedTemporaryFile().name
        self._create_po_file(filename, entries)

        g = GenerateQualityReports()
        g.transonly_po_and_extract_text(filename, tempfile.NamedTemporaryFile().name, text_file)

        return self._read_text_file(text_file)


    def test_transonly_po_and_extract_text_spaces(self):
        entries = list()
        entries.append(polib.POEntry(msgid='Hello\tThis is a test with tab',
                       msgstr='Hola\tAixò és una prova amb tab'))

        entries.append(polib.POEntry(msgid='Hello\tThis is a test with brs',
                       msgstr='Això<br>és una<br/>prova'))

        lines = self._generate_po_and_extract(entries)
        self.assertEquals("Hola Això és una prova amb tab\n", lines[0])
        self.assertEquals("Això és una prova\n", lines[2])

    def test_transonly_po_and_extract_text_accelerator(self):
        entries = list()
        entries.append(polib.POEntry(msgid='This is a test',
                       msgstr='_Això &és una prova~'))

        lines = self._generate_po_and_extract(entries)
        self.assertEquals("Això és una prova\n", lines[0])

    def test_transonly_po_and_extract_text_tags(self):
        entries = list()
        entries.append(polib.POEntry(msgid='This is a test',
                       msgstr='Això és una <b>prova<b>'))

        lines = self._generate_po_and_extract(entries)
        self.assertEquals("Això és una prova\n", lines[0])

    def test_transonly_po_and_extract_text_plural(self):
        entries = list()
        msgstr_plural = {}
        msgstr_plural[0] = 'Voleu suprimir aquesta fotografia de la càmera?'
        msgstr_plural[1] = 'Voleu suprimir aquestes %d fotografies de la càmera?'

        entries.append(polib.POEntry(msgid='Delete this photo from camera?',
                       msgid_plural='Delete these %d photos from camera?',
                       msgstr_plural=msgstr_plural))

        lines = self._generate_po_and_extract(entries)
        self.assertEquals("Voleu suprimir aquesta fotografia de la càmera?\n", lines[0])
        self.assertEquals("Voleu suprimir aquestes %d fotografies de la càmera?\n", lines[2])

    def test_transonly_po_and_extract_text_sphinx(self):
        entries = list()
        entries.append(polib.POEntry(msgid=":kbd:`R` sets the selection to 'replace' in the tool options, "
                                           ":menuselection:`Select --> Show Global Selection Mask`",
                                     msgstr=":kbd:`R` estableix la selecció a «Substitueix» a les Opcions de l'eina. "
                                            ":menuselection:`Selecciona --> Mostra la màscara de selecció global`"))

        lines = self._generate_po_and_extract(entries)
        self.assertEquals("R estableix la selecció a «Substitueix» a les Opcions de l'eina. "
                          "Selecciona --> Mostra la màscara de selecció global\n", lines[0])

    def test_transonly_po_and_extract_text_gnome_image(self):
        entries = list()
        entries.append(polib.POEntry(msgid="@@image: 'figures/a-z.gif'; md5=0df765cb06d1873c4b77ccfa2aec273a",
                                     msgstr="@@image: 'figures/a-z.gif'; md5=0df765cb06d1873c4b77ccfa2aec273a"))

        lines = self._generate_po_and_extract(entries)
        self.assertEquals(0, len(lines))

    def test_transonly_po_and_extract_text_gnome_external_image(self):
        entries = list()
        entries.append(polib.POEntry(msgid="external ref='figures/brasero-main-window.png' "
                                           "md5='11e5cc148d7c8c8dc0c63e68b2f611f3'",
                                     msgstr="external ref='figures/brasero-main-window.png' "
                                            "md5='11e5cc148d7c8c8dc0c63e68b2f611f3'"))

        lines = self._generate_po_and_extract(entries)
        self.assertEquals(0, len(lines))

    def test_transonly_po_and_extract_text_shpinx_image(self):
        entries = list()
        entries.append(polib.POEntry(msgid=".. image:: images/icons/Krita_mouse_right.png",
                                     msgstr=".. image:: images/icons/Krita_mouse_right.png"))

        lines = self._generate_po_and_extract(entries)
        self.assertEquals(0, len(lines))


if __name__ == '__main__':
    unittest.main()
