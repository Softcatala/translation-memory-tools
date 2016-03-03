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

from math import ceil
import urllib.parse

class Pagination(object):
    ''' Model object that manages the pagination of results'''

    def __init__(self, per_page, total_count, url):
        self.per_page = per_page
        self.total_count = total_count
        self.page = self._get_current_page(url)
        self.url = self._remove_page_query_string(url)

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def _remove_page_query_string(self, url):
        u = urllib.parse.urlparse(url)
        query = urllib.parse.parse_qs(u.query)
        query.pop('page', None)
        u = u._replace(query=urllib.parse.urlencode(query, True))
        return urllib.parse.urlunparse(u)

    def _get_current_page(self, url):
        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        if 'page' in parsed:
            page = int(parsed['page'][0])
        else:
            page = 1

        return page

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
