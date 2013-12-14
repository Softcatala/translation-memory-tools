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
        
        try:
            open_html()

            if len(term) < 2:
                write_html_header(term, 0, 0)
                print "<p>Avís: el text a cercar ha de tenir un mínim d'un caràcter</p>"
                return

            start_time = time.time()

            ix = open_dir(self.dir_name)
            with ix.searcher() as searcher:

                if org is True:
                    qs = u'source:{0}'.format(term)
                else:
                    qs = u'target:{0}'.format(term)

                if project is not None and project != 'tots':
                    if project == 'softcatala':
                        qs += u' softcatala:true'
                    else:
                        qs += u' project:{0}'.format(project)

                query = MultifieldParser(["source", "project", "softcatala"],
                                         ix.schema).parse(qs)

                results = searcher.search(query, limit=None)
                my_cf = WholeFragmenter()
                results.fragmenter = my_cf

                end_time = time.time() - start_time            
                write_html_header(term, len(results), end_time)
                
                for result in results:
                    self.print_result(result, org)
                    
        except Exception as details:
            print "Error:" + str(details)

def open_html():
    print 'Content-type: text/html\n\n'
    print '<html><head>'
    print '<meta http-equiv="content-type" content="text/html; charset=UTF-8">'
    print '<link rel="stylesheet" type="text/css" href="recursos.css" media="screen" />'

def write_html_header(term, results, time):
    t = term.encode('utf-8')
    print '<span class = \'searched\'>Resultats de la cerca del terme:</span><span class = \'searched-term\'> ' + t + '</span></br>'
    print '<p>{0} resultats. Temps de cerca: {1} segons</p>'.format(results, time)
    print '<a href = "./index.html">< Torna a la pàgina anterior</a></br></br>'


def main():

    form = cgi.FieldStorage()
    term = form.getvalue("query", '')
    where = form.getvalue("where", None)
    project = form.getvalue("project", None)
    
    if where == 'source':
        org = True
    else:
        org = False
   
    term = unicode(term, 'utf-8')

    search = Search()
    search.search(term, org, project)
    print '</head><body>'

if __name__ == "__main__":
    main()
