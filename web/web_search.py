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
import traceback
import json
from resultshighlight import *


class JsonSerializer:

    def do(self, search):

        print 'Content-type: application/json\n\n'

        results = search.get_results()

        all_results = []
        for result in results:
            all_results.append(result.fields())

        print json.dumps(all_results, indent=4, separators=(',', ': '))


class WebSerializer:

    def print_result(self, result, org, clean):

        print '<div class = "result">'
        print "<b>Projecte:</b> " + result["project"].encode('utf-8')
        print "<br>"

        if 'comment' in result.fields() and result["comment"] is not None and len(result["comment"]) > 0:
            print "<b>Comentari:</b> " + cgi.escape(result["comment"].encode('utf-8'))
            print "<br>"

        if 'context' in result.fields() and result["context"] is not None and len(result["context"]) > 0:
            print "<b>Context:</b> " + cgi.escape(result["context"].encode('utf-8'))
            print "<br>"

        if org is True:
            if clean is True:
                highlighted = ResultsHighlight.get(result["source"], result["source_clean"], result.highlights("source_clean")) 
            else:
                highlighted = result.highlights("source") 
                
            print "<b>Original:</b> " + highlighted.encode('utf-8')
            
            #print "<b>Original:</b> " + result.highlights("source").encode('utf-8')
            print "<br>"
            print "<b>Traducció:</b> " + cgi.escape(result["target"].encode('utf-8'))
        else:
            if clean is True:
                highlighted = ResultsHighlight.get(result["target"], result["target_clean"], result.highlights("target_clean")) 
            else:
                highlighted = result.highlights("target") 
            
            print "<b>Original:</b> " + cgi.escape(result["source"].encode('utf-8'))
            print "<br>"
            print "<b>Traducció:</b> " + highlighted.encode('utf-8')

        print '</div>'

    def do(self, search):
        '''
            Search a term in the Whoosh index
        '''

        try:
            self.open_html()

            if len(search.term) < 2:
                self.write_html_header(search.term, 0, 0)
                print "<p>Avís: el text a cercar ha de tenir un mínim d'un caràcter</p>"
                return

            start_time = time.time()

            results = search.get_results()
            end_time = time.time() - start_time

            self.write_html_header(search.term, results.scored_length(), end_time)
            for result in results:
                self.print_result(result, search.org, search.clean)

            self.close_html()

        except Exception as details:
            print "Error:" + str(details)
            traceback.print_exc()

    def open_html(self):
        print 'Content-type: text/html\n\n'
        print '<html><head>'
        print '<title>Resultats de la cerca</title>'
        print '<meta http-equiv="content-type" content="text/html; charset=UTF-8">'
        print '<meta name="robots" content="noindex, nofollow">'
        print '<link rel="stylesheet" type="text/css" href="recursos.css" media="screen" />'
        print '</head><body>'

    def write_html_header(self, term, results, time):
        t = term.encode('utf-8')
        print '<span class = \'searched\'>Resultats de la cerca del terme:</span><span class = \'searched-term\'> ' + t + '</span><br>'
        print '<p>{0} resultats. Temps de cerca: {1} segons</p>'.format(results, time)
        print '<a href = "./memories.html"> &lt; Torna a la pàgina anterior</a><br><br>'

    def close_html(self):
        print '</body></html>'


class Search:
    '''
            Search a term in the Whoosh index
    '''

    dir_name = "indexdir"

    def __init__(self, term, org, project, clean):
        self.term = term
        self.org = org
        self.project = project
        self.searcher = None
        self.query = None
        self.clean = clean

    def get_results(self):
        if self.searcher is None:
            self.search()

        results = self.searcher.search(self.query, limit=5000)
        my_cf = WholeFragmenter()
        results.fragmenter = my_cf
        return results

    def search(self):
        ix = open_dir(self.dir_name)
        self.searcher = ix.searcher()

        if self.org is True:
            if self.clean is True:
                qs = u'source_clean:{0}'.format(self.term)
            else:
                qs = u'source:{0}'.format(self.term)
        else:
            if self.clean is True:
                qs = u'target_clean:{0}'.format(self.term)
            else:
                qs = u'target:{0}'.format(self.term)
    
        if self.project is not None and self.project != 'tots':
            if self.project == 'softcatala':
                qs += u' softcatala:true'
            else:
                qs += u' project:{0}'.format(self.project)

        self.query = MultifieldParser(["source", "source_clean",
                                      "target", "target_clean",
                                      "project", "softcatala"],
                                      ix.schema).parse(qs)


def main():

    form = cgi.FieldStorage()
    term = form.getvalue("query", '')
    where = form.getvalue("where", None)
    project = form.getvalue("project", None)
    json = form.getvalue("json", None)
    clean_qs = form.getvalue("clean", None)    

    if clean_qs == 'on':
        clean = True
    else:
        clean = False

    if where == 'source':
        org = True
    else:
        org = False

    term = unicode(term, 'utf-8')

    search = Search(term, org, project, clean)

    if (json is None):
        web_serializer = WebSerializer()
        web_serializer.do(search)
    else:
        json_serializer = JsonSerializer()
        json_serializer.do(search)

if __name__ == "__main__":
    main()
