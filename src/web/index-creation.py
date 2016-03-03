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
import time
from optparse import OptionParser

import pystache

from indexcreator import IndexCreator


def process_template(template, filename, ctx):
    # Load template and process it.
    template = open(template, 'r').read()
    parsed = pystache.Renderer()
    s = parsed.render(template, ctx)

    # Write output.
    f = open(filename, 'w')
    f.write(s)
    f.close()


def read_parameters():
    parser = OptionParser()

    parser.add_option('-d', '--directory',
                      action='store', type='string', dest='po_directory',
                      default='../builder',
                      help='Directory to find the PO files')

    parser.add_option('-k', '--keyword',
                      action='store', type='string', dest='debug_keyword',
                      default=None,
                      help='Output debug information for a source keyword (for '
                      'debugging)')

    parser.add_option('-p',
                      '--projects',
                      action='store',
                      type='string',
                      dest='projects_names',
                      help='To restrict the processing of projects to comma'
                      ' separated given list (for debugging)')

    (options, args) = parser.parse_args()

    projects_names = None

    if options.projects_names is not None:
        projects_names = options.projects_names.split(',')

    return options.po_directory, options.debug_keyword, projects_names


def main():
    """Create a Whoosh index for a PO file.

    Given a PO file, enumerates all the strings, and creates a Whoosh index to
    be able to search later.
    """
    print("Create Whoosh index from a PO file")
    print("Use --help for assistance")

    start_time = time.time()

    try:
        locale.setlocale(locale.LC_ALL, '')
    except Exception as detail:
        print("Exception: " + str(detail))

    po_directory, debug_keyword, projects_names = read_parameters()
    indexCreator = IndexCreator(po_directory, debug_keyword, projects_names)
    indexCreator.create()
    indexCreator.process_projects()

    ctx = {
        'date': datetime.date.today().strftime("%d/%m/%Y"),
        'projects': str(indexCreator.projects),
        'words': locale.format("%d", indexCreator.words, grouping=True),
    }
    process_template("templates/statistics.mustache", "statistics.html", ctx)

    ctx = {
        # This is the list of projects to display for the user to select.
        'options': sorted(indexCreator.options, key=lambda x: x.lower()),
    }
    process_template("templates/select-projects.mustache",
                     "select-projects.html", ctx)

    end_time = time.time() - start_time
    print("time used to create the index: " + str(end_time))


if __name__ == "__main__":
    main()
