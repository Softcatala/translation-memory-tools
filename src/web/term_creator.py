#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2023 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import ijson
from optparse import OptionParser
from glossarysql import database, Entry


class TermCreator(object):
    def __init__(self, json_file):
        self.json_file = json_file
        self.database_file = json_file.replace(".json", "") + ".db3"
        self.entries = 0
        self.entries_indexed = 0

    def process_entries(self):
        with open(self.json_file) as json_fh:
            objects = ijson.items(json_fh, "item")
            for o in objects:
                self.write_entry(
                    o["term"],
                    o["translation"],
                    o["frequency"],
                    o["percentage"],
                    o["termcat"],
                )
                self.entries += 1

        self.save_index()

    def write_entry(self, source_term, translation, frequency, percentage, termcat):
        db_entry = Entry()
        db_entry.term = source_term
        db_entry.translation = translation
        db_entry.frequency = frequency
        db_entry.percentage = percentage
        db_entry.termcat = termcat
        db_entry.save()
        self.entries_indexed += 1

    def save_index(self):
        database.close()

    def create(self):
        name = self.database_file
        database.create(name)
        database.create_schema()


def read_parameters():
    parser = OptionParser()

    parser.add_option(
        "-f",
        "--filename",
        action="store",
        type="string",
        dest="filename",
        default="glossary.json",
        help="Json with the data to process",
    )

    (options, args) = parser.parse_args()
    return options.filename


def main():
    print("Creates a db3 database from a terminology JSON dump")
    print("Use --help for assistance")

    json_filename = read_parameters()
    termCreator = TermCreator(json_filename)
    termCreator.create()
    termCreator.process_entries()
    print(
        f"Total entries read {termCreator.entries}, indexed {termCreator.entries_indexed}"
    )
    print(f"Wrote {termCreator.database_file} file")


if __name__ == "__main__":
    main()
