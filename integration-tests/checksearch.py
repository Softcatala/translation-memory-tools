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

import json
import urllib.request


class CheckSearch(object):
    """Check if the search capabilities of the site work as expected"""

    def __init__(self, url):
        self.url = url

    def search_source(self, term):
        url = '{0}/tm/api/memory/search?source={1}&project=tots'
        url = url.format(self.url, term)

        urllib.request.urlretrieve(url, 'file.txt')
        with open('file.txt') as json_data:
            data = json.load(json_data)
            return data

    def search_glossary(self, term):
        url = '{0}/tm/api/glossary/search?source={1}&project=tots'
        url = url.format(self.url, term)

        urllib.request.urlretrieve(url, 'file.txt')
        with open('file.txt') as json_data:
            data = json.load(json_data)
            return data

    def _assert_contains(self, actual, expected):
        actual = actual.lower()
        expected = expected.lower()
        if expected not in actual:
            text = u"Expected '{0}' contains '{1}"
            raise Exception(text.format(expected, actual))

    def _assert_that(self, actual, expected):
        actual = actual.lower()
        expected = expected.lower()
        if not expected == actual:
            text = u"Expected '{0}' equals '{1}'"
            raise Exception(text.format(expected, actual))

    def _assert_greater(self, actual, minimum):
        if minimum > actual:
            text = u'Expected {0} to be greater than minimum {1}'
            raise Exception(text.format(minimum, actual))

    def _check_integration_data(self):
        string = (u'Palindromics numbers remain the same when its digits are '
                  u'reversed')
        data = self.search_source(string)

        self._assert_greater(len(data), 1)
        self._assert_that(data[0]['source'], string)
        self._assert_that(data[0]['target'],
                          u'Els nombres capicua no varien quan les '
                          u'seves xifres s\'inverteixen')
        self._assert_that(data[0]['context'], u'Palindromics.context')
        self._assert_contains(data[0]['comment'],
                              u'n.t.: títol de preferències')
        self._assert_contains(data[0]['comment'],
                              u'translators: comment for translators')

    def _check_common_searches(self):
        string = u'File'
        data = self.search_source(string)

        self._assert_greater(len(data), 1)
        self._assert_contains(data[0]['source'], string)

    def _check_glossary_source_search(self):
        string = u'file'
        data = self.search_glossary(string)

        self._assert_greater(len(data), 1)
        self._assert_contains(data[0]['term'], string)

    def check(self):
        try:
            self._check_common_searches()
            self._check_integration_data()
            self._check_glossary_source_search()
            return True
        except Exception as detail:
            print('Error checking search results: ' + detail)
            return False
