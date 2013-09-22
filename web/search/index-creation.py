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

import polib
import time
from whoosh.fields import *
from whoosh.index import create_in


class Search:

    dir_name = "indexdir"

    def create_index(self):
        '''
            Given a PO file, enumerates all the strings, and creates a Whoosh
            index to be able to search later
        '''

        ix = None
        start_time = time.time()

        schema = Schema(source=TEXT(stored=True), target=TEXT(stored=True),
                        comment=TEXT(stored=True))

        ix = create_in(self.dir_name, schema)
        writer = ix.writer()

        input_po = polib.pofile("tm.po")
        for entry in input_po:
            u = unicode(entry.msgstr)
            writer.add_document(source=entry.msgid, target=u)

        writer.commit()
        end_time = time.time() - start_time
        print "time used to create the index: " + str(end_time)


def main():

    print "Create Whoosh index from a PO file"
    search = Search()
    search.create_index()

if __name__ == "__main__":
    main()
