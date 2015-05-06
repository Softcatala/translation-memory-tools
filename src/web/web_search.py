#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2014-2015 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from flask import Flask, request, Response
import cgi
import json
import time
import sys
from jinja2 import Environment, FileSystemLoader
from urlparse import urlparse

sys.path.append('models/')
from pagination import Pagination
from glossary import Glossary
from search import Search


class JsonSerializer(object):

    def do(self, search):
        results = search.get_results()
        all_results = []
        for result in results:
            all_results.append(result.fields())

        return Response(json.dumps(all_results, indent=4,
                        separators=(',', ': ')),  mimetype='application/json')


class JsonSerializerGlossary(object):

    def do(self, results):
        all_results = []

        if results is not None:
            for result in results:
                all_results.append(result.dict)

        return Response(json.dumps(all_results, indent=4,
                        separators=(',', ': ')),  mimetype='application/json')


class WebSerializer(object):

    def _get_result_text(self, result, key):
        highlighted = result.highlights(key)
        if highlighted is not None and len(highlighted) > 0:
            return highlighted

        return cgi.escape(result[key])

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
            comment = cgi.escape(result["comment"]).replace('\n', '<br />').replace('\r', '')
            result_dict['comment'] = comment

        if 'context' in result.fields() and result["context"] is not None and len(result["context"]) > 0:
            result_dict['context'] = cgi.escape(result["context"])

        return result_dict

    def do(self, search):
        """Search a term in the Whoosh index."""
        aborted_search = False
        results = []
        num_results = 0
        total_time = 0
        PER_PAGE = 100

        g = Glossary()
        glossary = g.search(search.source)

        if search.has_invalid_search_term:
            aborted_search = True
            pagination = None
        else:
            start_time = time.time()
            raw_results = search.get_results()
            total_time = time.time() - start_time
            num_results = raw_results.scored_length()

            if len(raw_results) > 0:

                url = request.url.encode('utf-8')
                o = urlparse(url)
                url = '?' + o.query

                pagination = Pagination(PER_PAGE, len(raw_results), url)
                start = (pagination.page - 1) * PER_PAGE
                end = start

                max_end = start + PER_PAGE
                if num_results - start < max_end:
                    end += num_results - start
                else:
                    end += PER_PAGE

                for i in xrange(start, end):
                    results.append(self.get_result(raw_results[i]))
            else:
                pagination = None

        ctx = {
            'source': search.source,
            'target': search.target,
            'project': search.project,
            'results': results,
            'num_results': num_results,
            'time': "{:.2f}".format(total_time),
            'aborted_search': aborted_search,
            'glossary': glossary,
            'pagination': pagination,
        }

        env = Environment(loader=FileSystemLoader('./'))
        template = env.get_template('templates/search_results.html')

        r = template.render(ctx).encode('utf-8')
        return r


app = Flask(__name__)


@app.route('/')
def search_request():
    source = request.args.get('source')
    target = request.args.get('target')
    project = request.args.get('project')
    json = request.args.get('json')
    glossary_only = request.args.get('glossary_only')
    search = Search(source, target, project)

    serializer_cls = WebSerializer
    if json is not None:
        serializer_cls = JsonSerializer

    result = None
    if glossary_only is not None:
        glossary = Glossary()
        glossary = glossary.search(source)
        serializer = JsonSerializerGlossary()
        result = serializer.do(glossary)
    else:
        serializer = serializer_cls()
        result = serializer.do(search)

    return result

if __name__ == '__main__':
    app.debug = True
    app.run()
