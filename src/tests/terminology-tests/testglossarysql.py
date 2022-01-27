# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from terminology.glossarysql import *
import unittest


class TesGlossarySql(unittest.TestCase):

    SOURCE_TERM = "Hello"
    TRANSLATION = "Hola"
    FREQUENCY = 10
    PERCENTATGE = 5
    TERMCAT = True

    @classmethod
    def setUpClass(cls):
        name = ":memory:"
        database.create(name)
        database.create_schema()

        db_entry = cls._get_entry(cls)
        db_entry.save()
    

    def _get_entry(self):
        db_entry = Entry()
        db_entry.term = self.SOURCE_TERM
        db_entry.translation = self.TRANSLATION
        db_entry.frequency = self.FREQUENCY
        db_entry.percentage = self.PERCENTATGE
        db_entry.termcat = self.TERMCAT
        return db_entry 


    def test_save_glossary(self):
        glossary = Entry.select().where(Entry.term == self.SOURCE_TERM)
        cnt = glossary.count()

        item  = list(glossary)[0]
        self.assertEquals(1, cnt)
        self.assertEquals(self.SOURCE_TERM, item.term)
        self.assertEquals(self.TRANSLATION, item.translation)
        self.assertEquals(self.FREQUENCY, item.frequency)
        self.assertEquals(self.PERCENTATGE, item.percentage)
        self.assertEquals(self.TERMCAT, item.termcat)

    def test_fields(self):
        POS_ONLY_ITEM = 0
        glossary = Entry.select().where(Entry.term == self.SOURCE_TERM)
        result = list(glossary)[POS_ONLY_ITEM]

        values = result.dict.items()
        self.assertTrue(("id", "1") in values)
        self.assertTrue(("term", self.SOURCE_TERM) in values)
        self.assertTrue(("translation", self.TRANSLATION) in values)
        self.assertTrue(("frequency", str(self.FREQUENCY)) in values)
        self.assertTrue(("percentage", "5.0") in values)
        self.assertTrue(("termcat", "1") in values)

if __name__ == '__main__':
    unittest.main()
