#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2013 Jordi Mas i Hernandez <jmas@softcatala.org>
# Copyright (c) 2014 Leandro Regueiro Iglesias <leandro.regueiro@gmail.com>
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
import json
import time
import traceback

from whoosh.analysis import *
from whoosh.fields import *
from whoosh.highlight import *
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser


class JsonSerializer(object):

    def do(self, search):
        print('Content-type: application/json\n\n')
        results = search.get_results()
        all_results = []
        for result in results:
            all_results.append(result.fields())
        print(json.dumps(all_results, indent=4, separators=(',', ': ')))


class WebSerializer(object):

    def _get_result_text(self, source, highlighted):
        if highlighted is not None and len(highlighted) > 0:
            return highlighted.encode('utf-8')

        return cgi.escape(source.encode('utf-8'))

    def _get_formatted_comment(self, comment):
        """Return the comment adapted to properly integrate into HTML.

        Comments can be multi-line because they contain multiple lines or
        because we concatenated tcomments with comments from the PO.
        """
        return comment.replace('\n', '<br />').replace('\r', '')

    def print_result(self, result):
        print('<div class="result">')
        print('<table class="result-table">')
        print '<tr>'
        print "<td><b>Projecte:</b></td>" + "<td>" + result["project"].encode('utf-8') + "<td/>"
        print "</tr>"

        if 'comment' in result.fields() and result["comment"] is not None and len(result["comment"]) > 0:
            print '<tr>'
            comment = self._get_formatted_comment(cgi.escape(result["comment"])).encode('utf-8') 
            print "<td><b>Comentaris:</b></td>" + "<td>" + comment + "</td>"
            print '</tr>'

        if 'context' in result.fields() and result["context"] is not None and len(result["context"]) > 0:
            print '<tr>'
            print "<td><b>Context:</b></td>" + "<td>" + cgi.escape(result["context"].encode('utf-8')) + "</td>"
            print '</tr>'

        print '<tr>'
        print "<td><b>Original:</b></td>" + "<td>" + self._get_result_text(result["source"], result.highlights("source")) + "</td>"
        print '</tr>'

        print '<tr>'
        print "<td><b>Traducció:</b></td>" + "<td>" + self._get_result_text(result["target"], result.highlights("target")) + "</td>" 
        print '</tr>'

        print "</table></div>"

    def do(self, search):
        """Search a term in the Whoosh index."""
        try:
            self.open_html()

            if search.has_invalid_search_term:
                self.write_html_header(search.search_term_display, 0, 0)
                print("<p>Avís: el text a cercar ha de tenir un mínim d'un caràcter</p>")
            else:
                start_time = time.time()
                results = search.get_results()
                end_time = time.time() - start_time

                self.write_html_header(search.search_term_display,
                                       results.scored_length(), end_time)
                for result in results:
                    self.print_result(result)

            self.close_html()
        except Exception as details:
            traceback.print_exc()
            print str(details)

    def open_html(self):
        print 'Content-type: text/html\n\n'
        print '<html><head>'
        print '<title>Resultats de la cerca</title>'
        print '<meta http-equiv="content-type" content="text/html; charset=UTF-8">'
        print '<meta name="robots" content="noindex, nofollow">'
        print('<link type="text/css" rel="stylesheet" media="screen" href="recursos.css" />')
        print '</head><body>'

    def write_html_header(self, term, results, time):
        print '<span class="searched">Resultats de la cerca del terme:</span><span class="searched-term"> ' + term + '</span><br>'
        print '<p>{0} resultats. Temps de cerca: {1} segons</p>'.format(results, time)
        print '<a href="./memories.html"> &lt; Torna a la pàgina anterior</a><br /><br />'

    def close_html(self):
        print '</body></html>'


class Search(object):
    """Search a term in the Whoosh index."""
    dir_name = "indexdir"

    def __init__(self, source, target, project):
        self.source = source
        self.target = target
        self.project = project
        self.searcher = None
        self.query = None

    @property
    def has_invalid_search_term(self):
        return ((self.source is None or len(self.source) < 2) and
                (self.target is None or len(self.target) < 2))

    @property
    def search_term_display(self):
        text = ''

        if self.source is not None and len(self.source) > 0:
            text += self.source

        if self.target is not None and len(self.target) > 0:
            text += ' ' + self.target

        return text.encode('utf-8')

    def get_results(self):
        if self.searcher is None:
            self.search()

        results = self.searcher.search(self.query, limit=5000)
        results.fragmenter = WholeFragmenter()
        return results

    def search(self):
        ix = open_dir(self.dir_name)
        self.searcher = ix.searcher()
        fields = []

        qs = ''

        if self.source is not None and len(self.source) > 0:
            qs += u' source:{0}'.format(self.source)
            fields.append("source")

        if self.target is not None and len(self.target) > 0:
            qs += u' target:{0}'.format(self.target)
            fields.append("target")

        if self.project is not None and self.project != 'tots':
            if self.project == 'softcatala':
                qs += u' softcatala:true'
                fields.append("softcatala")
            else:
                qs += u' project:{0}'.format(self.project)
                fields.append("project")

        self.query = MultifieldParser(fields, ix.schema).parse(qs)


def main():
    form = cgi.FieldStorage()
    source = form.getvalue("source", '')
    target = form.getvalue("target", None)
    project = form.getvalue("project", None)
    json = form.getvalue("json", None)

    if source is not None:
        source = unicode(source, 'utf-8')

    if target is not None:
        target = unicode(target, 'utf-8')

    search = Search(source, target, project)

    if json is None:
        web_serializer = WebSerializer()
        web_serializer.do(search)
    else:
        json_serializer = JsonSerializer()
        json_serializer.do(search)


if __name__ == "__main__":
    main()
