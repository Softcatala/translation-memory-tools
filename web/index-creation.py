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

import locale
import datetime
import time
from optparse import OptionParser
from indexcreator import IndexCreator


def _write_statistics(projects, words):

    today = datetime.date.today()
    html = u'<p>L\'índex va ser actualitzat per últim cop el ' + today.strftime("%d/%m/%Y")
    html += u' i conté ' + str(projects) + ' projectes amb un total de '
    html += locale.format("%d", words, grouping=True) + ' paraules</p>'
    html_file = open("statistics.html", "w")
    html_file.write(html.encode('utf-8'))
    html_file.close()


def _write_select_projects(options):

    html = u'<p>Àmbit de cerca: '
    html += u'<select name ="project">\r'
    html += u'<option value="tots" selected="selected">Tots els projectes</option>\r'
    html += u'<option value="softcatala">Tots els projectes de Softcatalà</option>\r'

    options = sorted(options, key=lambda x: x.lower())
    for option in options:
        html += u'<option value="{0}">Projecte {1}</option>\r'.format(option, option)

    html += u'</select></p>\r'
    html_file = open("select-projects.html", "w")
    html_file.write(html.encode('utf-8'))
    html_file.close()


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
