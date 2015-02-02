#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2013-2015 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import sys

from jinja2 import Environment, FileSystemLoader
from whoosh.highlight import WholeFragmenter
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser

sys.path.append('../terminology')
from glossarysql import Entry, database


class JsonSerializer(object):

    def do(self, search):
        results = search.get_results()
        all_results = []
        for result in results:
            all_results.append(result.fields())

        print('Content-type: application/json\n\n')
        print(json.dumps(all_results, indent=4, separators=(',', ': ')))


class JsonSerializerGlossary(object):

    def do(self, results):
        all_results = []

        if results is not None:
            for result in results:
                all_results.append(result.dict)

        print('Content-type: application/json\n\n')
        print(json.dumps(all_results, indent=4, separators=(',', ': ')))


class Glossary(object):

    def search(self, search_term_display):
        try:
            database.open('glossary.db3')
            glossary = Entry.select().where(Entry.term == search_term_display)

            if glossary.count() == 0:
                glossary = None

        except:
            glossary = None

        return glossary


class WebSerializer(object):

    def _get_result_text(self, result, key):
        highlighted = result.highlights(key)
        if highlighted is not None and len(highlighted) > 0:
            return highlighted

        return result[key]

    def get_result(self, result):
        result_dict = {
            'source': self._get_result_text(result, "source"),
            'target': self._get_result_text(result, "target"),
            'project': result["project"],
            'comment': None,
            'context': None,
        }

        if 'comment' in result.fields() and result["comment"] is not None and len(result["comment"]) > 0:
            # Comments can be multi-line because they contain multiple lines or
            # because we concatenated tcomments with comments from the PO. So
            # it is necessary to adapt it to properly integrate into HTML.
            comment = result["comment"].replace('\n', '<br />').replace('\r', '')
            result_dict['comment'] = comment

        if 'context' in result.fields() and result["context"] is not None and len(result["context"]) > 0:
            result_dict['context'] = result["context"]

        return result_dict

    def do(self, search):
        """Search a term in the Whoosh index."""
        try:
            aborted_search = False
            results = []
            num_results = 0
            end_time = 0

            g = Glossary()
            glossary = g.search(search.search_term_display)

            if search.has_invalid_search_term:
                aborted_search = True
            else:
                start_time = time.time()
                raw_results = search.get_results()
                end_time = time.time() - start_time
                num_results = raw_results.scored_length()

                for result in raw_results:
                    results.append(self.get_result(result))

            ctx = {
                'search_term': search.search_term_display,
                'results': results,
                'num_results': num_results,
                'time': end_time,
                'aborted_search': aborted_search,
                'glossary': glossary,
            }

            env = Environment(loader=FileSystemLoader('./'))
            template = env.get_template('templates/search_results.html')

            print('Content-type: text/html\n\n')
            print(template.render(ctx).encode('utf-8'))
        except Exception as details:
            traceback.print_exc()
            print(str(details))


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

        return text

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
    glossary_only = form.getvalue("glossary_only", None)

    source = unicode(source, 'utf-8')

    if target is not None:
        target = unicode(target, 'utf-8')

    search = Search(source, target, project)

    serializer_cls = WebSerializer
    if json is not None:
        serializer_cls = JsonSerializer

    if glossary_only is not None:
        glossary = Glossary()
        glossary = glossary.search(source)
        serializer = JsonSerializerGlossary()
        serializer.do(glossary)
    else:
        serializer = serializer_cls()
        serializer.do(search)


if __name__ == "__main__":
    main()
