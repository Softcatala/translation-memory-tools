#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2013-2014 Jordi Mas i Hernandez <jmas@softcatala.org>
# Copyright (c) 2014 Leandro Regueiro Iglesias <leandro.regueiro@gmail.com>
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

import datetime
import locale
import json
from optparse import OptionParser
from indexcreator import IndexCreator


def read_parameters():
    parser = OptionParser()

    parser.add_option(
        "-f",
        "--filename",
        action="store",
        type="string",
        dest="filename",
        default="index_data.json",
        help="Json with the data to process",
    )

    (options, args) = parser.parse_args()
    return options.filename


def write_index_json(ctx):
    content = json.dumps(ctx, indent=4)
    with open("index.json", "w") as file:
        file.write(content)


def main():
    print("Create Whoosh index from a JSON file")
    print("Use --help for assistance")

    try:
        locale.setlocale(locale.LC_ALL, "")
    except Exception as detail:
        print("Exception: " + str(detail))

    start_time = datetime.datetime.now()

    json_filename = read_parameters()
    indexCreator = IndexCreator(json_filename)
    indexCreator.create()
    indexCreator.process_entries()

    ctx = {
        "date": datetime.date.today().strftime("%d/%m/%Y"),
        "projects": str(indexCreator.get_projects_count()),
        "words": locale.format_string(
            "%d", indexCreator.get_words_count(), grouping=True
        ),
    }
    write_index_json(ctx)

    print(
        f"Total sentences read {indexCreator.sentences}, indexed {indexCreator.sentences_indexed}"
    )

    print(f"Time used to create the index: {datetime.datetime.now() - start_time}")


if __name__ == "__main__":
    main()
