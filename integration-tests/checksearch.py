#!/usr/bin/env python2
# -*- coding: utf-8 -*-
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

import urllib
import json


class CheckSearch:
    '''Check if the search capabilities of the site work as expected'''

    def __init__(self, url):
        self.url = url

    def search_source(self, term):

        url = '{0}/web_search.py?query={1}&where=translation&project=tots&json=1'.format(self.url, term)

        urllib.urlretrieve(url, 'file.txt')
        with open('file.txt') as json_data:
            data = json.load(json_data)
            return data

    def check(self):

        try:

            word = 'fitxer'
            data = self.search_source(word)
            if len(data) == 0:
                print "No results"
                return False

            if data[0]['target'].lower() != word:
                print 'No {0} word found'.format(word)
                return False

            return True

        except Exception as detail:
            print "Error: " + str(detail)
            return False
