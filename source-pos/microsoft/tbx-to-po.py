#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
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

import xml.etree.ElementTree as ET
import polib

def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)


def main():
    """Converts TBX to PO"""
    pofile = polib.POFile()
    pofile.metadata = {
        'Project-Id-Version': '1.0',
        'Report-Msgid-Bugs-To': 'nobody@nobody',
        'POT-Creation-Date': '2007-10-18 14:00+0100',
        'PO-Revision-Date': '2007-10-18 14:00+0100',
        'Last-Translator': 'microsoft@microsoft.com',
        'Language-Team': 'Microsoft',
        'Language': 'ca',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
        'Plural-Forms': 'nplurals=2; plural=n != 1;'
    }

    tree = ET.parse('MicrosoftTermCollection.tbx')
    root = tree.getroot()
    terms = 0

    # Gets all the list of terms
    for term_entry in root.iter('termEntry'):
        # English terms appear only once but an English term can have more than
        # one translation (e.g.: "home page")
        source = ''
        targets = []
        description = ''
        term_ids = []
        is_source = True

        # Process a single term
        for term_subitems in term_entry:
            for i in term_subitems.iter():
                if i.tag == 'descrip':
                    description = i.text
                elif i.tag == 'langSet':
                    lang = i.get('{http://www.w3.org/XML/1998/namespace}lang')
                    is_source = lang == 'en-US'
                elif i.tag == 'term':
                    if is_source:
                        source = i.text
                    else:
                        targets.append(i.text)
                        term_ids.append(i.get('id'))

        terms += len(targets)

        for i in range(len(targets)):
            entry = polib.POEntry(msgid=source, msgstr=targets[i], tcomment=description, msgctxt=term_ids[i])
            pofile.append(entry)

    filename = "microsoft-terms.po"
    pofile.save(filename)
    line_prepender(filename, "# See Microsoft license terms for this file: https://www.microsoft.com/Language/en-US/LicenseAgreement.aspx")
    print("Terms : " + str(terms))


if __name__ == "__main__":
    main()
