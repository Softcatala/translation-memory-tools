#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2013-2014 Jordi Mas i Hernandez <jmas@softcatala.org>
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


class Option(object):

    def __init__(self, option):
        self.option = option


def _process_template(template, filename, variables):
    # Load template and process it
    template = open(template, 'r').read()
    parsed = pystache.Renderer()
    s = parsed.render(unicode(template, "utf-8"), variables)

    # Write output
    f = open(filename, 'w')
    f.write(s.encode("utf-8"))
    f.close()


def _write_statistics(projects, words):
    variables = {}
    today = datetime.date.today()
    variables['date'] = today.strftime("%d/%m/%Y")
    variables['projects'] = str(projects)
    variables['words'] = locale.format("%d", words, grouping=True)
    _process_template("statistics.mustache", "statistics.html", variables)


def _write_select_projects(project_names):
    variables = {}
    options = []
    for project_name in sorted(project_names, key=lambda x: x.lower()):
         options.append(Option(project_name))

    variables['options'] = options
    _process_template("select-projects.mustache", "select-projects.html", variables)


def read_parameters():
    po_directory = None
    debug_keyword = None
    projects_names = None

    parser = OptionParser()

    parser.add_option('-d', '--directory',
                      action='store', type='string', dest='po_directory',
                      default='../src/',
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

    po_directory = options.po_directory

    if options.debug_keyword is not None:
        debug_keyword = options.debug_keyword

    if options.projects_names is not None:
        projects_names = options.projects_names.split(',')

    return po_directory, debug_keyword, projects_names


def main():
    '''
        Given a PO file, enumerates all the strings, and creates a Whoosh
        index to be able to search later
    '''
    print "Create Whoosh index from a PO file"
    print "Use --help for assistance"

    start_time = time.time()

    try:
        locale.setlocale(locale.LC_ALL, '')
    except Exception as detail:
        print "Exception: " + str(detail)

    po_directory, debug_keyword, projects_names = read_parameters()
    indexCreator = IndexCreator(po_directory)
    indexCreator.debug_keyword = debug_keyword
    indexCreator.projects_names = projects_names
    indexCreator.create()
    indexCreator.process_projects()

    _write_statistics(indexCreator.projects, indexCreator.words)
    _write_select_projects(indexCreator.options)

    end_time = time.time() - start_time
    print "time used to create the index: " + str(end_time)


if __name__ == "__main__":
    main()
