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

import cgi
import time

from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser


class Search:

    dir_name = "indexdir"

    def search(self, term):
        '''
            Search a term in the Whoosh index
        '''
        ix = None
        start_time = time.time()

        ix = open_dir(self.dir_name)
        with ix.searcher() as searcher:
            query = QueryParser("target", ix.schema).parse(term)
            results = searcher.search(query)
            for result in results:
                print result["source"] + "</br>"
                print result.highlights("target").encode('utf-8')
                print "</br></br>"

        end_time = time.time() - start_time
        print "Temps: " + str(end_time)


def main():

    print 'Content-type: text/html\n\n'

    form = cgi.FieldStorage()
    term = form.getvalue("query", u'instal·lació')

    print '<html><head>'
    print '<meta http-equiv="content-type" content="text/html; charset=UTF-8">'
    print 'Terme de cerca: ' + term + '</br></br>'
    search = Search()
    term = unicode(term, 'utf-8')
    search.search(term)
    print '</head><body>'

if __name__ == "__main__":
    main()
