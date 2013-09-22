#!/usr/bin/env python
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
sys.path.append('../../src/')

import polib
import time
import os
from whoosh.fields import *
from whoosh.index import create_in
from jsonbackend import JsonBackend

class Search:

    dir_name = "indexdir"
    writer = None
    
    def process_projects(self):

        json = JsonBackend("../../src/projects.json")
        json.load()

        for project_dto in json.projects:        
            self._process_project(project_dto.name, project_dto.filename)

    def _process_project(self, name, filename):

        full_filename = os.path.join("../../latest-memories/po/", filename)
        print "Processing: " + full_filename
        
        try:
            input_po = polib.pofile(full_filename)
            
            for entry in input_po:
                s = unicode(entry.msgid)
                t = unicode(entry.msgstr)
                c = unicode(entry.comment)
                p = unicode(name)
                self.writer.add_document(source=s, target=t, comment=c, project=p)

        except Exception as detail:
            print "Exception: " +  str(detail)

    def create_index(self):

        schema = Schema(source=TEXT(stored=True), target=TEXT(stored=True),
                        comment=TEXT(stored=True), project=TEXT(stored=True))
                        
        if not os.path.exists(self.dir_name):
            os.mkdir(self.dir_name)

        ix = create_in(self.dir_name, schema)
        self.writer = ix.writer()


def main():
    '''
        Given a PO file, enumerates all the strings, and creates a Whoosh
        index to be able to search later
    '''

    print "Create Whoosh index from a PO file"
    start_time = time.time()
    
    search = Search()
    search.create_index()
    search.process_projects()
    search.writer.commit()
    
    end_time = time.time() - start_time
    print "time used to create the index: " + str(end_time)

if __name__ == "__main__":
    main()
