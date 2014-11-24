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
# Boston, MA 02111-1307,

from builder.projectmetadatadto import ProjectMetaDataDto
import unittest
import datetime


class TestProjectMetaDataDto(unittest.TestCase):

    def test_set_get_last_translation_update(self):
        DATE = datetime.datetime(2010, 8, 3, 23, 33, 9, 890000)
        metadata_dto = ProjectMetaDataDto('')
        metadata_dto.last_translation_update = DATE
        self.assertEquals(DATE, metadata_dto.last_translation_update)

    def test_set_last_translation_update_not_set(self):
        metadata_dto = ProjectMetaDataDto('')
        self.assertEquals(None, metadata_dto.last_translation_update)

    def test_set_last_translation_update_wrong_type(self):
        metadata_dto = ProjectMetaDataDto('')
        date = 1
        with self.assertRaises(TypeError):
            metadata_dto.last_translation_update(date)

    def test_set_get_last_fetch(self):
        DATE = datetime.datetime(2010, 8, 3, 23, 33, 9, 890000)
        metadata_dto = ProjectMetaDataDto('')
        metadata_dto.last_fetch = DATE
        self.assertEquals(DATE, metadata_dto.last_fetch)

    def test_set_last_fetch_update_not_set(self):
        metadata_dto = ProjectMetaDataDto('')
        self.assertEquals(None, metadata_dto.last_fetch)

    def test_set_last_fetch_update_wrong_type(self):
        metadata_dto = ProjectMetaDataDto('')
        date = 1
        with self.assertRaises(TypeError):
            metadata_dto.last_fetch(date)


if __name__ == '__main__':
    unittest.main()
