#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2015 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import pystache
import json


class Target(object):

    def __init__(self, target):
        self.target = target


class Translation(object):

    def __init__(self, source, target):
        self.source = source
        self.target = target


def read_po_file(filename):
    input_po = polib.pofile(filename)
    translations = []

    for entry in input_po:
        if entry.translated() is False:
            continue

        translation = Translation(entry.msgid, entry.msgstr)
        translations.append(translation)

    return translations


def process_template(template, filename, ctx):
    template = open(template, 'r').read()
    parsed = pystache.Renderer()
    s = parsed.render(template, ctx)

    f = open(filename, 'w')
    f.write(s)
    f.close()


def _load_iso_files(filename):
    if filename is None:
        return None

    with open(filename) as json_data:
        data = json.load(json_data)

    return data


class IsoEntry(object):

    def __init__(self, name, link, description):
        self.name = name
        self.link = link
        self.description = description


def main():

    print ("Generates Html files from a list of PO files")

    iso_files = _load_iso_files('iso-files.json')
    isos_list = []

    for key in iso_files.keys():
        iso_file = iso_files[key]
        _input = iso_file['input']
        template = iso_file['template']
        output = iso_file['output']
        title = iso_file['title']
        text = iso_file['text']

        translations = read_po_file(_input)

        ctx = {
            'entries': translations,
            'title': title,
            'text': text,
        }

        process_template(template, output, ctx)

        iso_entry = IsoEntry(key, output, title)
        isos_list.append(iso_entry)

    ctx = {
        'entries': isos_list,
    }
    process_template('isos-list.mustache', 'isos_list.html', ctx)

if __name__ == "__main__":
    main()
