# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import sqlite3
import logging
from .projectmetadatadto import ProjectMetaDataDto


class ProjectMetaDataDao(object):
    NAME = 0
    LAST_FETCH = 1
    TRANSLATION_UPDATE = 2
    WORDS = 3
    CHECKSUM = 4

    def __init__(self):
        self.connection = None

    def create_model(self):
        c = self.connection.cursor()
        command = (
            "CREATE TABLE IF NOT EXISTS projects ("
            "name TEXT PRIMARY KEY,"
            "last_fetch TIMESTAMP,"
            "last_translation_update TIMESTAMP,"
            "words INTEGER,"
            "checksum TEXT"
            ");"
        )
        c.execute(command)

        command = "CREATE INDEX IF NOT EXISTS [ix_name] ON [projects] ([name]);"
        c.execute(command)
        self.connection.commit()

    def open(self, database_name):
        self.connection = sqlite3.connect(
            database_name, detect_types=sqlite3.PARSE_DECLTYPES
        )
        self.create_model()

    def put(self, dto):
        c = self.connection.cursor()
        command = "INSERT OR REPLACE INTO 'projects' VALUES (?, ?, ?, ?, ?);"
        c.execute(
            command,
            (
                dto.name,
                dto.last_fetch,
                dto.last_translation_update,
                dto.words,
                dto.checksum,
            ),
        )
        self.connection.commit()

    def get(self, name):
        c = self.connection.cursor()
        result = c.execute("SELECT * FROM projects WHERE name=?", (name,))
        row = result.fetchone()

        if row is None:
            return None

        dto = ProjectMetaDataDto(row[self.NAME])
        dto.last_fetch = row[self.LAST_FETCH]
        dto.last_translation_update = row[self.TRANSLATION_UPDATE]
        dto.words = row[self.WORDS]
        dto.checksum = row[self.CHECKSUM]
        return dto

    def get_all(self):
        c = self.connection.cursor()
        command = "SELECT * FROM projects"
        result = c.execute(command)
        rows = result.fetchall()
        return self._fetch_all(rows)

    def _fetch_all(self, rows):
        entries = []
        if rows is None:
            return entries

        for row in rows:
            dto = ProjectMetaDataDto(row[self.NAME])
            dto.last_fetch = row[self.LAST_FETCH]
            dto.last_translation_update = row[self.TRANSLATION_UPDATE]
            dto.words = row[self.WORDS]
            dto.checksum = row[self.CHECKSUM]
            entries.append(dto)

        return entries

    def delete_last_fetch(self, days):
        c = self.connection.cursor()
        command = (
            "DELETE FROM projects WHERE last_fetch <= date('now','-{0} day')".format(
                days
            )
        )
        result = c.execute(command)
        self.connection.commit()
        logging.info(f"Projects clean up {result.rowcount}")

    def dump(self):
        c = self.connection.cursor()
        command = "SELECT * FROM projects"
        result = c.execute(command)
        print("Database rows")
        for row in result:
            print(row)

    def close(self):
        self.connection.close()
