#!/usr/bin/env python
# -*- encoding: utf-8 -*-
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

import xml.etree.ElementTree as ET
import polib
import fnmatch
import os

def _find(directory, pattern):
    filelist = []

    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                filelist.append(filename)

    filelist.sort()
    return filelist

def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)


def _process_entries_from_file(lg_filename, pofile):
    terms = 0
    tree = ET.parse(lg_filename)
    root = tree.getroot()
    sources = set()

    # Gets all the list of terms
    for term_entry in root.iter('TranslationSet'):

        # Process a single term
        source = None
        target = None
        for term_subitems in term_entry:
            for i in term_subitems.iter():
                if i.tag == 'base':
                    source = i.text
                elif i.tag == 'tran':
                    target = i.text

        if source in sources:
            continue

        sources.add(source)

        msgctxt = os.path.basename(lg_filename)
        entry = polib.POEntry(msgid=source, msgstr=target, msgctxt=msgctxt)
        pofile.append(entry)
        terms = terms + 1

    return terms

    #print("Terms : " + str(terms))
#    line_prepender(filename, "# See Microsoft license terms for this file: https://www.microsoft.com/Language/en-US/LicenseAgreement.aspx")

def main():
    print("Convert Apple Glot(lg) files to PO files")

    terms = 0
    files = 0
    pofile = polib.POFile()
    pofile.metadata = {
        'Project-Id-Version': '1.0',
        'Report-Msgid-Bugs-To': 'nobody@nobody',
        'POT-Creation-Date': '2016-10-18 14:00+0100',
        'PO-Revision-Date': '2016-10-18 14:00+0100',
        'Last-Translator': 'apple@apple.com',
        'Language-Team': 'Apple',
        'Language': 'ca',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
        'Plural-Forms': 'nplurals=2; plural=n != 1;'
    }

    for filename in _find('glossaries/', '*.lg'):
        terms += _process_entries_from_file(filename, pofile)
        files = files + 1

    filename = "ios.po"
    pofile.save(filename)
    print('Processed {0} files, {1} terms'.format(files, terms))


if __name__ == "__main__":
    main()
