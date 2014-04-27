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
sys.path.append('../src/')

import polib
import os
from whoosh.fields import *
from whoosh.index import create_in
from whoosh.analysis import StandardAnalyzer
from jsonbackend import JsonBackend
from cleanstring import CleanString
from cleanupfilter import CleanUpFilter

class IndexCreator:

    def __init__(self, po_directory):
        self.dir_name = "indexdir"
        self.writer = None
        self.words = 0
        self.projects = 0
        self.options = []
        self.sentences_indexed = 0
        self.sentences = 0
        self.po_directory = po_directory
        self.debug_keyword = None
        self.projects_names = None


    def process_projects(self):

        json = JsonBackend("../src/projects.json")
        json.load()

        for project_dto in json.projects:

            if self.projects_names:
                found = False

                for project_name in self.projects_names:
                    project_dto_lower = project_dto.name.lower().strip()
                    if project_name.lower().strip() == project_dto_lower:
                        found = True

                if not found:
                    continue

            if project_dto.selectable is True:
                self.options.append(project_dto.name)

            self._process_project(project_dto.name,
                                  project_dto.filename,
                                  project_dto.softcatala)
            self.projects = self.projects + 1

        print 'Total sentences {0}, indexed {1}'.format(self.sentences, 
              self.sentences_indexed)
        
        self.writer.commit()


    def _get_comment(self, entry):
        '''
            PO files can contain 3 types of comments:
         
                # translators comments
                #. extracted 
                #: location

            We import only translator's comments and extracted that we concatenate
            to make it transparent to the search
        '''

        if (entry.tcomment is None):
            comment = entry.tcomment
        else:
            comment = unicode(entry.tcomment)

        if entry.comment is not None:
            if entry.tcomment is None:
                comment = unicode(entry.comment)
            else:
                comment += u'\r\n' + unicode(entry.comment)

        return comment

    def _process_project(self, name, filename, softcatala):

        full_filename = os.path.join(self.po_directory, filename)
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

                c = self._get_comment(entry)
                
                if t is None or len(t) == 0:
                    # msgstr_plural is a dictionary where the key is the index and
                    # the value is the localised string
                    if entry.msgstr_plural is not None and len(entry.msgstr_plural) > 0:
                        t = unicode(entry.msgstr_plural["0"])
                        t_clean = CleanString.get_strip(t)
                       
                if self.debug_keyword is not None and self.debug_keyword.strip() == s:
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

        analyzer = StandardAnalyzer(minsize=MIN_WORDSIZE_TO_IDX, stoplist=None) | CleanUpFilter()
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

