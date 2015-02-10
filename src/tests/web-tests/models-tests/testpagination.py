#!/usr/bin/env python2
# -*- coding: utf-8 -*-
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

import unittest

from web.models.pagination import Pagination


class TestPagination(unittest.TestCase):

    def test_page(self):
        pagination = Pagination(50, 100, 'http://www.softcatala.org/web_search.py?page=2')
        self.assertEquals(pagination.page, 2)

    def test_url(self):
        pagination = Pagination(50, 100, 'http://www.softcatala.org/web_search.py?page=2&project=gnome')
        self.assertEquals(pagination.url, 'http://www.softcatala.org/web_search.py?project=gnome')

    def test_pages_one(self):
        pagination = Pagination(50, 10, '')
        self.assertEquals(pagination.pages, 1)

    def test_pages_three(self):
        pagination = Pagination(50, 101, '')
        self.assertEquals(pagination.pages, 3)

    def test_has_prev_true(self):
        pagination = Pagination(50, 100, 'http://www.softcatala.org/web_search.py?page=2')
        self.assertTrue(pagination.has_prev)

    def test_has_prev_false(self):
        pagination = Pagination(50, 1, '')
        self.assertFalse(pagination.has_prev)

    def test_has_next_true(self):
        pagination = Pagination(50, 100, '')
        self.assertTrue(pagination.has_next)

    def test_has_next_false(self):
        pagination = Pagination(50, 1, '')
        self.assertFalse(pagination.has_next)

if __name__ == '__main__':
    unittest.main()
