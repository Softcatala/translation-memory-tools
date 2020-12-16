# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Jordi Mas i Hernandez <jmas@softcatala.org>
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


class CheckStats(object):
    """Check if the search capabilities of the site work as expected"""

    def __init__(self, url):
        self.url = url

    def _check_stats(self):
        url = '{0}stats?date=2010-01-01'
        url = url.format(self.url)
        urllib.request.urlretrieve(url, 'file.txt')
        with open('file.txt') as json_data:
            data = json.load(json_data)

        self._assert_greater(data['total_words'], 0)
        self._assert_greater(data['projects'], 0)

    def _assert_greater(self, actual, minimum):
        if minimum > actual:
            text = u'Expected {0} to be greater than minimum {1}'
            raise Exception(text.format(minimum, actual))

    def check(self):
        try:
            self._check_stats()
            return True
        except Exception as detail:
            print('Error checking stats: ' + str(detail))
            return False
