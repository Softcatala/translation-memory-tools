#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2013-2023 Jordi Mas i Hernandez <jmas@softcatala.org>
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
from builder.postojson import POsToJson


def read_parameters():
    parser = OptionParser()

    parser.add_option(
        "-d",
        "--directory",
        action="store",
        type="string",
        dest="po_directory",
        default=".",
        help="Directory to find the PO files",
    )

    parser.add_option(
        "-k",
        "--keyword",
        action="store",
        type="string",
        dest="debug_keyword",
        default=None,
        help="Output debug information for a source keyword (for " "debugging)",
    )

    parser.add_option(
        "-p",
        "--projects",
        action="store",
        type="string",
        dest="projects_names",
        help="To restrict the processing of projects to comma"
        " separated given list (for debugging)",
    )

    (options, args) = parser.parse_args()

    projects_names = None

    if options.projects_names is not None:
        projects_names = options.projects_names.split(",")

    return options.po_directory, options.debug_keyword, projects_names


def write_index_json(ctx):
    content = json.dumps(ctx, indent=4, separators=(",", ": "))
    with open("index.json", "w") as file:
        file.write(content)


def main():
    print(
        "Exports a JSON based on collections of PO to later index the export into a db storage"
    )
    print("Use --help for assistance")

    start_time = datetime.datetime.now()

    try:
        locale.setlocale(locale.LC_ALL, "")
    except Exception as detail:
        print("Exception: " + str(detail))

    po_directory, debug_keyword, projects_names = read_parameters()
    toJson = POsToJson(po_directory, debug_keyword, projects_names)
    toJson.process_projects()

    ctx = {
        "date": datetime.date.today().strftime("%d/%m/%Y"),
        "projects": str(toJson.projects),
        "words": locale.format_string("%d", toJson.words, grouping=True),
    }
    write_index_json(ctx)

    print(
        "Time used to export the JSON: {0} ".format(
            datetime.datetime.now() - start_time
        )
    )


if __name__ == "__main__":
    main()
