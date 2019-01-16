# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import xml.etree.ElementTree as ET
import polib


class ConvertTmx():

    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

    def convert(self):
        pofile = polib.POFile()

        pofile.metadata = {
            'Project-Id-Version': '1.0',
            'Report-Msgid-Bugs-To': 'none',
            'POT-Creation-Date': '2007-10-18 14:00+0100',
            'PO-Revision-Date': '2007-10-18 14:00+0100',
            'Last-Translator': 'none@none.org',
            'Language-Team': 'Catalan <info@none.org>',
            'MIME-Version': '1.0',
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
            'Plural-Forms': 'nplurals=2; plural=n != 1;',
        }

        tree = ET.parse(self.input_file)
        root = tree.getroot()
        sources = set()

        entries = 0
        for tu_entry in root.iter('tu'):
            source = ''
            translation = ''
            for tuv_entry in tu_entry:
                if tuv_entry.tag != 'tuv':
                    continue

                llengua = tuv_entry.attrib['{http://www.w3.org/XML/1998/namespace}lang']

                for seg_entry in tuv_entry.iter('seg'):
                    if llengua == 'en' or llengua == 'en-US':
                        source = seg_entry.text
                    elif llengua == 'ca':
                        translation = seg_entry.text

            if source is None or source is '':
                continue

            if translation is None or translation is '':
                continue

            if source in sources:
                msgctxt = str(entries)
            else:
                msgctxt = None
                sources.add(source)

            entry = polib.POEntry(msgid=source, msgstr=translation,
                                  msgctxt=msgctxt)
            pofile.append(entry)
            entries = entries + 1

        pofile.save(self.output_file)
