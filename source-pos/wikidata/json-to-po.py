#!/usr/bin/env python2
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

# yajl2 has 25% better performance than ijson default backend
import ijson.backends.yajl2 as ijson
import datetime
import json
import urllib
import polib


def percentage(part, whole):
    return 100 * float(part)/float(whole)


def exists_in_tm(term):
    try:
        url = u'http://localhost:8081/tm/api/memory/search?source=\"{1}\"&project=tots'
        url = url.format(url, term)

        urllib.urlretrieve(url.encode('utf-8'), 'file.txt')
        with open('file.txt') as json_data:
            data = json.load(json_data)

        return len(data)
    except Exception as e:
        print ("Cannot open: {0}. Error: {1}".format(url.encode("utf-8"), e))
        return 0


def _create_empty_po_file():
    po_file = polib.POFile()
    po_file.check_for_duplicates = True

    po_file.metadata = {
        'Project-Id-Version': '1.0',
        'POT-Creation-Date': '2007-10-18 14:00+0100',
        'PO-Revision-Date': '2007-10-18 14:00+0100',
        'Last-Translator': 'Wikidata project',
        'Language-Team': 'Catalan <Wikidataproject>',
        'MIME-Version': '1.0',
        'Language: ca\n'
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
        'Plural-Forms': 'nplurals=2; plural=n != 1;',
    }
    return po_file

def _is_segment_valid(string):
    # Discard numeric strings only (like years)
    if string.isdigit():
        print ("Discarded: " + string.encode('utf-8'))
        return False

    # On char only (like 'A')
    if len(string) < 2:
        print ("Discarded: " + string.encode('utf-8'))
        return False

    return True

def _insert_entry_inpofile(po_file, entry):
    try:
        po_file.append(entry)

    except ValueError:
        pass


def _process_json(filename):
    if filename is None:
        return None

    cnt = 0
    selected = 0
    onlyArticles = True
    PO_NAME = 'wikidata.po'
    SAVE_INTERVAL = 1000
    PROCESS_NOF_ENTRIES = 2 * 1000 * 1000

    po_file = _create_empty_po_file()

    with open(filename, 'r') as json_data:
        value = ijson.items(json_data, 'item')

        for item in value:
            label = item.get('labels')
            if label is None:
                continue

            item_id = item['id']
            if onlyArticles is True:
                if item_id is None or item_id.startswith("Q") is False:
                    continue

            comment = u'Article {0}'.format(item_id)
            en_label = label.get('en')
            ca_label = label.get('ca')

            if en_label is None or ca_label is None:
                continue

            cnt = cnt + 1
            value = en_label['value']

            if _is_segment_valid(value) is False:
                continue

            exists = exists_in_tm(value)
            if exists > 0:
                selected = selected + 1
            else:
                continue

            entry = polib.POEntry(msgid=en_label['value'],
                                  msgstr=ca_label['value'],
                                  tcomment = comment + " (label)")

            _insert_entry_inpofile(po_file, entry)

            desc = item.get('descriptions')
            if desc is not None:
                en_desc = desc.get('en')
                ca_desc = desc.get('ca')

                if en_desc is not None and ca_desc is not None:
                    entry = polib.POEntry(msgid=en_desc['value'],
                                          msgstr=ca_desc['value'],
                                          tcomment = comment + " (description)")

                    _insert_entry_inpofile(po_file, entry)



            if cnt % SAVE_INTERVAL == 0:
                po_file.save(PO_NAME)

            if cnt > PROCESS_NOF_ENTRIES:
                break

    po_file.save(PO_NAME)
    print ("Total entries: " + str(cnt))
    print ("Selected: {0} (%{1})".format(str(selected), str(percentage(selected, cnt))))


# https://www.mediawiki.org/wiki/Wikibase/DataModel/Primer
def main():

    # Download data set from http://dumps.wikimedia.org/other/wikidata/
    # I tried using commons and mediawiki categories without great results
    # instead we choose a word if this appears on Softcatalà memories.
    print ("Reads a Wikidata json file and generates a PO files with the")
    print ("strings found in Softcatalà translation memory")

    start_time = datetime.datetime.now()
    _process_json('20150629.json')
    print ('Time {0}'.format(datetime.datetime.now() - start_time))

if __name__ == "__main__":
    main()
