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
from whoosh.highlight import *
from whoosh.qparser import MultifieldParser


class Search:

    dir_name = "indexdir"

    def print_result(self, result, org):

        print '<div class = "result">'
        print "<b>Projecte:</b> " + result["project"].encode('utf-8')
        print "</br>"

        if 'comment' in result.fields() and result["comment"] is not None and len(result["comment"]) > 0:
            print "<b>Comentari:</b> " + cgi.escape(result["comment"].encode('utf-8'))
            print "</br>"

        if 'context' in result.fields() and result["context"] is not None and len(result["context"]) > 0:
            print "<b>Context:</b> " + cgi.escape(result["context"].encode('utf-8'))
            print "</br>"

        if org is True:
            print "<b>Original:</b> " + result.highlights("source").encode('utf-8')
            print "</br>"
            print "<b>Traducció:</b> " + cgi.escape(result["target"].encode('utf-8'))
        else:
            print "<b>Original:</b> " + cgi.escape(result["source"].encode('utf-8'))
            print "</br>"
            print "<b>Traducció:</b> " + result.highlights("target").encode('utf-8')

        print '</div>'

    def search(self, term, org, project):
        '''
            Search a term in the Whoosh index
        '''

        start_time = time.time()

        ix = open_dir(self.dir_name)
        with ix.searcher() as searcher:

            if org is True:
                qs = 'source:{0}'.format(term)
            else:
                qs = 'target:{0}'.format(term)

            if project is not None and project != 'tots':
                if project == 'softcatala':
                    qs += ' softcatala:true'
                else:
                    qs += ' project:{0}'.format(project)

            query = MultifieldParser(["source", "project", "softcatala"],
                                     ix.schema).parse(qs)

            results = searcher.search(query, limit=None)
            my_cf = WholeFragmenter()
            results.fragmenter = my_cf
            for result in results:
                self.print_result(result, org)

        end_time = time.time() - start_time
        print str(len(results)) + " resultats. Temps de cerca: " + str(end_time)


def open_html(term):

    print 'Content-type: text/html\n\n'
    print '<html><head>'
    print '<meta http-equiv="content-type" content="text/html; charset=UTF-8">'
    print '<link rel="stylesheet" type="text/css" href="recursos.css" media="screen" />'
    print '<span class = \'searched\'>Resultats de la cerca del terme:</span><span class = \'searched-term\'> ' + term + '</span></br></br>'
    print '<a href = "/index.html">< Torna a la pàgina anterior</a></br></br>'


def main():

    form = cgi.FieldStorage()
    term = form.getvalue("query", None)
    where = form.getvalue("where", None)
    project = form.getvalue("project", None)

    open_html(term)
        
    if where == 'source':
        org = True
    else:
        org = False

    search = Search()
    term = unicode(term, 'utf-8')
    search.search(term, org, project)
    print '</head><body>'

if __name__ == "__main__":
    main()
