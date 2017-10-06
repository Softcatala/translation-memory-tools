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

from builder.projectmetadatadao import ProjectMetaDataDao
from builder.projectmetadatadto import ProjectMetaDataDto
import unittest
import datetime
from datetime import timedelta


class TestProjectMetaDataDao(unittest.TestCase):

    def test_get_non_existant(self):

        PROJECT_NAME = 'test project get'

        project_dao = ProjectMetaDataDao()
        project_dao.open(':memory:')
        read_project_dto = project_dao.get(PROJECT_NAME)

        self.assertEquals(None, read_project_dto)

    def test_put_newvalue(self):

        PROJECT_NAME = 'test project'

        project_dto = ProjectMetaDataDto(PROJECT_NAME)
        project_dto.last_fetch = datetime.datetime.now()
        project_dto.last_translation_update = datetime.datetime.now()

        project_dao = ProjectMetaDataDao()
        project_dao.open(':memory:')
        project_dao.put(project_dto)
        read_project_dto = project_dao.get(PROJECT_NAME)

        self.assertEquals(PROJECT_NAME, read_project_dto.name)

    def test_put_updatevalue(self):

        PROJECT_NAME = 'test project update'
        WORDS = 100

        project_dto = ProjectMetaDataDto(PROJECT_NAME)
        project_dto.last_fetch = datetime.datetime.now()
        project_dto.last_translation_update = datetime.datetime.now()

        project_dao = ProjectMetaDataDao()
        project_dao.open(':memory:')
        project_dao.put(project_dto)
        project_dto.words = WORDS
        project_dao.put(project_dto)

        read_project_dto = project_dao.get(PROJECT_NAME)

        self.assertEquals(WORDS, read_project_dto.words)

    def test_get_all(self):

        PROJECT_NAME = 'test project get_all'

        project_dto = ProjectMetaDataDto(PROJECT_NAME)
        project_dto.last_fetch = datetime.datetime.now()
        project_dto.last_translation_update = datetime.datetime.now()

        project_dto2 = ProjectMetaDataDto(PROJECT_NAME + "2")
        project_dto2.last_fetch = datetime.datetime.now()
        project_dto2.last_translation_update = datetime.datetime.now()

        project_dao = ProjectMetaDataDao()
        project_dao.open(':memory:')
        project_dao.put(project_dto)
        project_dao.put(project_dto2)

        project_dtos = project_dao.get_all()
        self.assertEquals(2, len(project_dtos))

    def test_get_all(self):

        PROJECT_NAME = 'test project get_all'

        project_dto = ProjectMetaDataDto(PROJECT_NAME)
        project_dto.last_fetch = datetime.datetime.now()
        project_dto.last_translation_update = datetime.datetime.now()

        project_dto2 = ProjectMetaDataDto(PROJECT_NAME + "2")
        project_dto2.last_fetch = datetime.datetime.now()
        project_dto2.last_translation_update = datetime.datetime.now()

        project_dao = ProjectMetaDataDao()
        project_dao.open(':memory:')
        project_dao.put(project_dto)
        project_dao.put(project_dto2)

        project_dtos = project_dao.get_all()
        self.assertEquals(2, len(project_dtos))

    def test_delete_last_fetch(self):

        PROJECT_NAME = 'test project delete'
        DAYS = 90

        project_dto = ProjectMetaDataDto(PROJECT_NAME)
        project_dto.last_fetch = datetime.datetime.now()
        project_dto.last_translation_update = datetime.datetime.now()

        project_dto2 = ProjectMetaDataDto(PROJECT_NAME + "2")
        project_dto2.last_fetch = datetime.datetime.now() - timedelta(days=DAYS + 1)
        project_dto2.last_translation_update = datetime.datetime.now()

        project_dao = ProjectMetaDataDao()
        project_dao.open(':memory:')
        project_dao.put(project_dto)
        project_dao.put(project_dto2)

        project_dao.delete_last_fetch(DAYS)
        project_dtos = project_dao.get_all()
        self.assertEquals(1, len(project_dtos))

if __name__ == '__main__':
    unittest.main()
