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
import html
import time
import sys
import urllib.parse
import datetime
from flask_cors import CORS, cross_origin

sys.path.append('models/')
from pagination import Pagination
from glossary import Glossary
from stats import Stats
from search import Search
from usage import Usage

app = Flask(__name__)
CORS(app)

class SearchAPIResults(object):

    def _get_result_text(self, result, key):
        highlighted = result.highlights(key)
        if highlighted is not None and len(highlighted) > 0:
            return highlighted

        return html.escape(result[key])

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
            comment = html.escape(result["comment"]).replace('\n', '<br />').replace('\r', '')
            result_dict['comment'] = comment

        if 'context' in result.fields() and result["context"] is not None and len(result["context"]) > 0:
            result_dict['context'] = html.escape(result["context"])

        return result_dict

    def do(self, search, page):
        """Search a term in the Whoosh index."""
        aborted_search = False
        results = []
        num_results = 0
        total_time = 0
        PER_PAGE = 100

        start_time = time.time()

        if search.has_invalid_search_term:
            aborted_search = True
            pagination = None
            glossary = None
        else:
            g = Glossary(search.source)
            g.search()
            glossary = g.get_results()

            raw_results = search.get_results()
            num_results = raw_results.scored_length()

            if len(raw_results) > 0:

                url = request.url
                o = urllib.parse.urlparse(url)
                url = '?' + o.query

                pagination = Pagination(PER_PAGE, len(raw_results), url, page)
                start = (pagination.page - 1) * PER_PAGE
                end = start

                max_end = start + PER_PAGE
                if num_results - start < max_end:
                    end += num_results - start
                else:
                    end += PER_PAGE

                for i in range(start, end):
                    results.append(self.get_result(raw_results[i]))

                pages = pagination.pages
            else:
                pagination = None
                pages = 0

        total_time = time.time() - start_time
        ctx = {
            'source': search.source,
            'target': search.target,
            'project': search.project,
            'num_results': num_results,
            'time': "{:.2f}".format(total_time),
            'aborted_search': aborted_search,
            'glossary': glossary,
            'pages': pages,
            'results': results,
        }

        return ctx


@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@app.route('/search', methods=['GET'])
def search_api():
    source = request.args.get('source')
    target = request.args.get('target')
    page = request.args.get('page')
    project = ','.join(request.args.getlist('project'))

    search = Search(source, target, project)
    results = SearchAPIResults()
    json = results.do(search, page)

    usage = Usage()
    usage.log()
    return json


@app.route('/glossary/search', methods=['GET'])
def glossary_search_api():
    source = request.args.get('source')

    glossary = Glossary(source)
    glossary.search()
    return Response(glossary.get_json(), mimetype='application/json')


@app.route('/memory/search', methods=['GET'])
def memory_search_api():
    source = request.args.get('source')
    target = request.args.get('target')
    project = request.args.get('project')

    search = Search(source, target, project)
    return Response(search.get_json(), mimetype='application/json')

@app.route('/stats', methods=['GET'])
def stats_api():
    requested = request.args.get('date')
    date_requested = datetime.datetime.strptime(requested, '%Y-%m-%d')
    stats = Stats()
    return Response(stats.get_json(date_requested), mimetype='application/json')

@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@app.route('/projects', methods=['GET'])
def projects_api():
    with open("projects.json" ,"r") as file:
        projects = file.read()

    return Response(projects, mimetype='text/plain')

@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@app.route('/index', methods=['GET'])
def index_api():
    with open("index.json" ,"r") as file:
        projects = file.read()

    return Response(projects, mimetype='text/plain')


if __name__ == '__main__':
    app.debug = True
    app.run()
