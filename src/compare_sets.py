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

import datetime
import os
from optparse import OptionParser

from builder.jsonbackend import JsonBackend
from builder.pofile import POFile


def process_projects(src_directory, trg_directory):
    json = JsonBackend("../cfg/projects/")
    json.load()

    projects = sorted(json.projects, key=lambda x: x.name.lower())
    for project_dto in projects:
        if project_dto.downloadable:
            src_file = os.path.join(src_directory, project_dto.filename)
            trg_file = os.path.join(trg_directory, project_dto.filename)

            if os.path.isfile(src_file) and not os.path.isfile(trg_file):
                print("{0} is missing in the new version".format(project_dto.filename))

            if not os.path.isfile(src_file) and os.path.isfile(trg_file):
                print(
                    "{0} has been added in the new version".format(project_dto.filename)
                )

            src_stats = POFile(src_file).get_statistics()
            trg_stats = POFile(trg_file).get_statistics()

            print(
                "{0} project: {1} words (before), {2} words (now), delta {3}".format(
                    project_dto.filename, src_stats, trg_stats, trg_stats - src_stats
                )
            )


def read_parameters():
    parser = OptionParser()

    parser.add_option(
        "-s",
        "--srcdir",
        action="store",
        type="string",
        dest="src_directory",
        help="Directory to find the PO files",
    )

    parser.add_option(
        "-t",
        "--trgdir",
        action="store",
        type="string",
        dest="trg_directory",
        help="Directory to find the TMX files",
    )

    (options, args) = parser.parse_args()

    if options.src_directory is None:
        parser.error("source directory not given")

    if options.trg_directory is None:
        parser.error("target directory not given")

    return (options.src_directory, options.trg_directory)


def main():
    print("Compares two sets of PO files and shows the difference")
    print("Use --help for assistance")
    print(datetime.datetime.now())

    src_directory, trg_directory = read_parameters()
    process_projects(src_directory, trg_directory)


if __name__ == "__main__":
    main()
