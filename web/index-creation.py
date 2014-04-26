#!/usr/bin/env python
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

import sys
import locale
sys.path.append('../src/')

import polib
import time
import os
from whoosh.fields import *
from whoosh.index import create_in
from whoosh.analysis import StandardAnalyzer
from jsonbackend import JsonBackend
from optparse import OptionParser
from cleanstring import CleanString
from cleanupfilter import CleanUpFilter

po_directory = None
debug_keyword = None
projects_names = None


class IndexCreator:

    dir_name = "indexdir"
    writer = None
    words = 0
    projects = 0
    options = []
    sentences_indexed = 0
    sentences = 0

    def process_projects(self, po_directory):

        global projects_names

        json = JsonBackend("../src/projects.json")
        json.load()

        for project_dto in json.projects:

            if projects_names:
                found = False

                for project_name in projects_names:
                    project_dto_lower = project_dto.name.lower().strip()
                    if project_name.lower().strip() == project_dto_lower:
                        found = True

                if not found:
                    continue

            if project_dto.selectable is True:
                self.options.append(project_dto.name)

            self._process_project(po_directory, project_dto.name,
                                  project_dto.filename,
                                  project_dto.softcatala)
            self.projects = self.projects + 1

        print 'Total sentences {0}, indexed {1}'.format(self.sentences, 
              self.sentences_indexed)

    def _process_project(self, po_directory, name, filename, softcatala):

        global debug_keyword

        full_filename = os.path.join(po_directory, filename)
        print "Processing: " + full_filename

        try:

            input_po = polib.pofile(full_filename)

            for entry in input_po:
                self.sentences += 1 
                s = unicode(entry.msgid)
                t = unicode(entry.msgstr)
                s_clean = CleanString.get_strip(s)
                t_clean = CleanString.get_strip(t)
                p = unicode(name)

                if (entry.msgctxt is None):
                    x = entry.msgctxt
                else:
                    x = unicode(entry.msgctxt)

                if (entry.tcomment is None):
                    c = entry.tcomment
                else:
                    c = unicode(entry.tcomment)

                if entry.comment is not None:
                    if entry.tcomment is None:
                        c = unicode(entry.comment) 
                    else:
                        c += u'\r\n' + unicode(entry.comment)

                if t is None or len(t) == 0:
                    # msgstr_plural is a dictionary where the key is the index and
                    # the value is the localised string
                    if entry.msgstr_plural is not None and len(entry.msgstr_plural) > 0:
                        t = unicode(entry.msgstr_plural["0"])
                        t_clean = CleanString.get_strip(t)
                       
                if debug_keyword is not None and debug_keyword.strip() == s:
                    print "Source: " + s
                    print "Translation: " + t
                    print "Context: " + str(x)
                    print "Comment: " + str(c)

                if s is None or len(s) == 0 or t is None or len(t) == 0:
                    continue    

                self.sentences_indexed += 1
                string_words = entry.msgstr.split(' ')
                self.words += len(string_words)
                self.writer.add_document(source=s, 
                                         target=t,
                                         source_clean = s_clean,
                                         target_clean = t_clean,
                                         comment=c,
                                         context=x, project=p,
                                         softcatala=softcatala)

        except Exception as detail:
          print "Exception: " + str(detail)


    def create(self):

        MIN_WORDSIZE_TO_IDX = 1

        analyzer=StandardAnalyzer(minsize=MIN_WORDSIZE_TO_IDX, stoplist=None) | CleanUpFilter()
        schema = Schema(source=TEXT(stored=True, analyzer=analyzer), 
                        target=TEXT(stored=True, analyzer=analyzer),
                        source_clean=TEXT(stored=True, analyzer=analyzer), 
                        target_clean=TEXT(stored=True, analyzer=analyzer),
                        comment=TEXT(stored=True), context=TEXT(stored=True),
                        softcatala=BOOLEAN(stored=True), project=TEXT(stored=True))

        if not os.path.exists(self.dir_name):
            os.mkdir(self.dir_name)

        ix = create_in(self.dir_name, schema)
        self.writer = ix.writer()


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

    global po_directory
    global debug_keyword
    global projects_names

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

    read_parameters()
    indexCreator = IndexCreator()
    indexCreator.create()
    indexCreator.process_projects(po_directory)
    indexCreator.writer.commit()

    _write_statistics(indexCreator.projects, indexCreator.words)
    _write_select_projects(indexCreator.options)

    end_time = time.time() - start_time
    print "time used to create the index: " + str(end_time)

if __name__ == "__main__":
    main()
