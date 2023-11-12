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


def main():
    print("Create Whoosh index from a JSON file")
    print("Use --help for assistance")

    start_time = datetime.datetime.now()

    json_filename = read_parameters()
    indexCreator = IndexCreator(json_filename)
    indexCreator.create()
    indexCreator.process_entries()

    print(
        "Time used to create the index: {0} ".format(
            datetime.datetime.now() - start_time
        )
    )


if __name__ == "__main__":
    main()
