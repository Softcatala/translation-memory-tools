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


import polib
from optparse import OptionParser

def get_metadata():
    metadata = {
        'Project-Id-Version': '1.0',
        'Report-Msgid-Bugs-To': 'info@softcatala.org',
        'POT-Creation-Date': '2007-10-18 14:00+0100',
        'PO-Revision-Date': '2007-10-18 14:00+0100',
        'Last-Translator': 'info@softcatala.org',
        'Language-Team': 'Catalan <info@softcatala.org>',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
        'Plural-Forms': 'nplurals=2; plural=n != 1;',
    }
    return metadata

def create_po_entry(source, target):

    s = unicode(source, 'utf-8')
    source = s[0].upper() + s[1:]

    t = unicode(target, 'utf-8')
    target = t[0].upper() + t[1:]

    entry = polib.POEntry(msgid=source, msgstr=target)
    return entry

def generate_for_tm(columns, pofile):

    if ((columns[2] == 'm' or columns[2] == 'f' or columns[2] == 'f pl'
       or columns[2] == 'm pl') and not '(' in columns[1] and not '|'
       in columns[1]):

        # A verb (,to) or 2 sources keywords: a, b
        if ',' in columns[0] or ',' in columns[1]:
            return

        entry = create_po_entry(columns[0], columns[1])

        pofile.append(entry)

def generate_for_glossary(columns, pofile):

    # Shallows the ", to" for verbs like in "abort, to"
    columns[0] = columns[0].replace(", to", '')

    source_terms = columns[0].split(',')
    source_terms = [term.strip() for term in source_terms]

    for term in source_terms:
        entry = create_po_entry(term, columns[1])
        pofile.append(entry)


def create_recull(tm_mode):

    cvsfile = open("recull.csv", "r")
    pofile = polib.POFile()
    pofile.metadata = get_metadata()

    total = 0
    for line in cvsfile:
        columns = line.split(';')
        columns = [col.strip() for col in columns]

        total += 1
        if not columns:
            continue

        # Process for TM usage
        if tm_mode is True:
            generate_for_tm(columns, pofile)
            continue

        # Process for usage as glossary
        generate_for_glossary(columns, pofile)

    if tm_mode:
        filename = 'recull.po'
    else:
        filename = 'recull-glossary.po'

    pofile.save(filename)
    print "Total entries: " + str(total)


def main():
    '''
        Given a PO file, enumerates all the strings, and creates a Whoosh
        index to be able to search later
    '''

    parser = OptionParser()

    parser.add_option(
        '-t',
        '--tm',
        action='store_true',
        dest='tm_mode',
        default=False,
        help=u'Generate glossary for usage as TM'
    )

    (options, args) = parser.parse_args()
    tm_mode = options.tm_mode
    print "TM mode is: " + str(tm_mode)
    create_recull(tm_mode)

if __name__ == "__main__":
    main()
