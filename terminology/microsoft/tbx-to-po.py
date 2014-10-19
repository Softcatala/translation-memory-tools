#!/usr/bin/env python
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


def get_metadata():
    metadata = {
        'Project-Id-Version': '1.0',
        'Report-Msgid-Bugs-To': 'nobody@nobody',
        'POT-Creation-Date': '2007-10-18 14:00+0100',
        'PO-Revision-Date': '2007-10-18 14:00+0100',
        'Last-Translator': 'microsoft@microsoft.com',
        'Language-Team': 'Microsoft',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
        'Plural-Forms': 'nplurals=2; plural=n != 1;',
    }
    return metadata


def read_xml():
    pofile = polib.POFile()
    pofile.metadata = get_metadata()

    tree = ET.parse('MicrosoftTermCollection.tbx')
    root = tree.getroot()
    terms = 0

    # Gets all the list of terms
    for term_entry in root.iter('termEntry'):
        # English terms appear only once but an English term can have more than
        # one translation (e.g.: "home page")
        source = ''
        targets = []
        is_source = True

        # Process a single term
        for term_subitems in term_entry:
            for i in term_subitems.iter():
                #print i.tag
                if i.tag == 'langSet':
                    lang = i.get('{http://www.w3.org/XML/1998/namespace}lang')
                    is_source = lang == 'en-US'
                elif i.tag == 'term':
                    if is_source:
                        source = unicode(i.text)
                    else:
                        targets.append(unicode(i.text))

        terms += len(targets)

        for target in targets:
            entry = polib.POEntry(msgid=source, msgstr=target)
            pofile.append(entry)

    pofile.save("microsoft-terms.po")
    print("Terms : " + str(terms))


def main():
    '''
        Converts TBX to PO
    '''
    read_xml()


if __name__ == "__main__":
    main()
