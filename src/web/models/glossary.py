#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2013-2015 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import sys

sys.path.append('../terminology')
from glossarysql import Entry, database
import json


class Glossary(object):

    def __init__(self, search_term):
        self.search_term = search_term
        self.glossary = None

    def get_results(self):
        return self.glossary

    def search(self):
        try:
            database.open('glossary.db3')
            self.glossary = Entry.select().where(Entry.term == self.search_term.lower())

            if self.glossary.count() == 0:
                self.glossary = None

        except:
            print("Cannot find glossary.db3")
            self.glossary = None

    def get_json(self):
        all_results = []

        if self.glossary is not None:
            for result in self.glossary:
                all_results.append(result.dict)

        return json.dumps(all_results, indent=4, separators=(',', ': '))
