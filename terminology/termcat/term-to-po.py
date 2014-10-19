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
        'Report-Msgid-Bugs-To': 'info@termcat.cat',
        'POT-Creation-Date': '2007-10-18 14:00+0100',
        'PO-Revision-Date': '2007-10-18 14:00+0100',
        'Last-Translator': 'info@termcat.cat',
        'Language-Team': 'Catalan <info@termcat.cat>',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
        'Plural-Forms': 'nplurals=2; plural=n != 1;',
    }
    return metadata


def read_xml():
    pofile = polib.POFile()
    pofile.metadata = get_metadata()

    tree = ET.parse('4sources_termes.xml')
    root = tree.getroot()
    terms = 0
    stored_terms = {}
    for term_entry in root.iter('fitxa'):
        # Text can be any order (en->ca) or (ca->en) and also you can
        # can have several en or ca strings
        sources = []
        translations = []

        informatica_term = False
        # This loops areatematica and denominacio tags
        for term_subentry in term_entry:
            if term_subentry.tag == 'areatematica':
                if u'TIC' in term_subentry.text:
                    informatica_term = True

            if not term_subentry.tag == 'denominacio':
                continue

            llengua = unicode(term_subentry.attrib['llengua'])
            if llengua == 'en':
                # Remove the indication that is a verb to facilitate matching
                term = term_subentry.text.replace(", to", '')
                sources.append(term)
            elif llengua == 'ca':
                translations.append(term_subentry.text)
            else:
                continue  # We are not interested in other languages

        if informatica_term is False:
            continue

        # For every English term available write an entry with the first Catalan
        # translation available
        for source in sources:
            source = unicode(source)
            translation = unicode(translations[0])

            if source in stored_terms and stored_terms[source] == translation:
                print(u'Skipping duplicated term: {0}'.format(source))
                continue

            stored_terms[source] = translation
            entry = polib.POEntry(msgid=source, msgstr=translation)
            pofile.append(entry)
            terms += 1

    pofile.save("termcat.po")
    print("Terms : " + str(terms))


def main():
    '''
        Converts TERMCAT 'TERM' own format to PO
    '''

    read_xml()


if __name__ == "__main__":
    main()
