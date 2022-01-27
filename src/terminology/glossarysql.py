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

from playhouse.shortcuts import model_to_dict
from peewee import SqliteDatabase, Model, TextField, IntegerField, FloatField
import os

# TODO: we use peewee and raw SQL projectmetadatadao. At some point may make
# sense to consolidate this

class SqliteDatabaseGlossary(SqliteDatabase):

    def create(self, database_name):
        if os.path.exists(database_name):
            os.remove(database_name)

        self.init(database_name)

    def open(self, database_name):
        self.init(database_name)

    def create_schema(self):
        self.connect()
        self.create_tables([Entry])
        self.begin()

    def close(self):
        self.commit()

database = SqliteDatabaseGlossary(None, autocommit=False)


class Entry(Model):
    '''Simple denormalized model to represent a glossary entry'''

    term = TextField(unique=False)
    translation = TextField(unique=False)
    frequency = IntegerField()
    percentage = FloatField()
    termcat = IntegerField()

    def _value_to_str(self, d):
        for key in d.keys():
            d[key] = str(d[key])

        return d

    @property
    def dict(self):
        d = model_to_dict(self)
        return self._value_to_str(d)

    class Meta:
        db_table = 'entries'
        database = database
