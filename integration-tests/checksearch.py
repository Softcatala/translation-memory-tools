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

        url = '{0}/web_search.py?query={1}&where=source&project=tots' \
              '&json=1'.format(self.url, term)

        urllib.urlretrieve(url, 'file.txt')
        with open('file.txt') as json_data:
            data = json.load(json_data)
            return data

    def _assert_contains(self, actual, expected):

        actual = actual.lower()
        expected = expected.lower()
        if expected not in actual:
            raise Exception(u"Expected '{0}' contains '{1}'".
                            format(expected, actual))

    def _assert_that(self, actual, expected):

        actual = actual.lower()
        expected = expected.lower()
        if not expected == actual:
            raise Exception(u"Expected '{0}' equals '{1}'".
                            format(expected, actual))

    def _assert_greater(self, actual, minimum):

        if minimum > actual:
            raise Exception(u'Expected {0} to be greater than minimum {1}'.
                            format(minimum, actual))

    def _check_integration_data(self):

        string = u'"Palindromics numbers remain the same when its digits are reversed"'
        data = self.search_source(string)

        self._assert_greater(len(data), 1)
        self._assert_that(data[0]['source'], u'Palindromics numbers remain the same when its digits are reversed')
        self._assert_that(data[0]['target'], u'Els nombres capicua no varien quan les seves xifres s\'inverteixen')
        self._assert_that(data[0]['context'], u'Palindromics.context')
        self._assert_contains(data[0]['comment'], u'Títol de preferències')

    def _check_common_seaches(self):

        string = u'File'
        data = self.search_source(string)

        self._assert_greater(len(data), 1)
        self._assert_contains(data[0]['source'], string)

    def check(self):

        try:

            self._check_common_seaches()
            self._check_integration_data()
            return True

        except Exception as detail:
            print u'Error: ' + unicode(detail)
            return False
