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

from web.indexcreator import IndexCreator
from web.models.search import Search


class TestSearch(unittest.TestCase):

    PROJECT = u'gnome'
    SC = True

    data_set = [
                u"Nox Documents Found", u"No s'han trobat", PROJECT, SC,
                u"No Documents Found Today", u"No s'han trobat documents avui", PROJECT, SC,
                u"No Documents Found late Yesterday", u"No s'han trobat documents ahir", PROJECT, SC]

    FIELDS = 4

    def _create_index(self):
        '''Creates an index in RAM with the entries from data_set array'''
        self.index = IndexCreator('')
        index = self.index.create(True)

        for idx in xrange(0, len(self.data_set), self.FIELDS):
            self.index.write_entry(source=self.data_set[idx + 0],
                                   target=self.data_set[idx + 1],
                                   comment=u'',
                                   context=u'',
                                   project=self.data_set[idx + 2],
                                   softcatala=self.data_set[idx + 3])

        self.index.writer.commit()
        return index

    def test_query_simple_query_source(self):
        ix = self._create_index()
        search = Search(u'Today', None, u'gnome')
        search.search(ix)
        results = search.get_results()

        self.assertEquals(len(results), 1)
        self.assertEquals(results[0]["source"], u"No Documents Found Today")

    def test_query_simple_with_or_query_source(self):
        ix = self._create_index()
        search = Search(u'Today OR Yesterday', None, u'gnome')
        search.search(ix)
        results = search.get_results()

        self.assertEquals(len(results), 2)
        self.assertEquals(results[0]["source"], u"No Documents Found Today")
        self.assertEquals(results[1]["source"], u"No Documents Found late Yesterday")

    def test_query_simple_with_not_query_source(self):
        ix = self._create_index()
        search = Search(u'Documents NOT Yesterday', None, u'gnome')
        search.search(ix)
        results = search.get_results()

        self.assertEquals(len(results), 2)
        for i in xrange(0, len(results)):
            self.assertFalse(u'Yesterday' in results[i]["source"])

    def test_query_simple_with_and_query_source(self):
        ix = self._create_index()
        search = Search(u'Documents AND late', None, u'gnome')
        search.search(ix)
        results = search.get_results()

        self.assertEquals(len(results), 1)
        self.assertEquals(results[0]["source"], u"No Documents Found late Yesterday")

    def test_query_source_target(self):
        ix = self._create_index()
        search = Search(u'Documents', u'Ahir', u'gnome')
        search.search(ix)
        results = search.get_results()

        self.assertEquals(len(results), 1)
        self.assertEquals(results[0]["source"], u"No Documents Found late Yesterday")

    def test_query_source_OR_target(self):
        ix = self._create_index()
        search = Search(u'Today OR No', u'trobat', u'gnome')
        search.search(ix)
        results = search.get_results()

        self.assertEquals(len(results), 2)
        self.assertEquals(results[0]["source"], u"No Documents Found Today")
        self.assertEquals(results[1]["source"], u"No Documents Found late Yesterday")


if __name__ == '__main__':
    unittest.main()
