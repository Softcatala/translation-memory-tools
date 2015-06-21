#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2015 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from whoosh.highlight import WholeFragmenter
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
import json


class Search(object):
    """Search a term in the Whoosh index."""
    dir_name = "indexdir"

    def __init__(self, source, target, project):
        self._source = source
        self._target = target
        self._project = project
        self.searcher = None
        self.query = None

    @property
    def has_invalid_search_term(self):
        return ((self.source is None or len(self.source) < 2) and
                (self.target is None or len(self.target) < 2))

    @property
    def source(self):
        return self._source

    @property
    def target(self):
        return self._target

    @property
    def project(self):
        return self._project

    def get_results(self):
        if self.searcher is None:
            self.search()

        results = self.searcher.search(self.query, limit=None)
        results.fragmenter = WholeFragmenter()
        return results

    def search(self, ix=None):

        if ix is None:
            ix = open_dir(self.dir_name)
            self.search(ix)

        self.searcher = ix.searcher()
        fields = []
        qs = ''

        # We use parenthesis to prevent operators like OR used in source
        # to affect target
        if self.source is not None and len(self.source) > 0:
            qs += u' source:({0})'.format(self.source)
            fields.append("source")

        if self.target is not None and len(self.target) > 0:
            qs += u' target:({0})'.format(self.target)
            fields.append("target")

        if self.project is not None and self.project != 'tots':
            if self.project == 'softcatala':
                qs += u' softcatala:true'
                fields.append("softcatala")
            else:
                qs += u' project:{0}'.format(self.project)
                fields.append("project")

        self.query = MultifieldParser(fields, ix.schema).parse(qs)

    def get_json(self):
        results = self.get_results()
        all_results = []
        for result in results:
            all_results.append(result.fields())

        return json.dumps(all_results, indent=4, separators=(',', ': '))
