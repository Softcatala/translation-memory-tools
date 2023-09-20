# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from unittest import TestCase, mock
from unittest.mock import Mock, MagicMock
from builder.projects import Projects
from builder.projectmetadatadao import ProjectMetaDataDao


class TestProjects(TestCase):
    def test_get_db_name(self):
        projects = Projects(False)

        with mock.patch.dict("os.environ", {"DB3_PATH": ""}):
            self.assertEqual("statistics.db3", projects._get_db_name())

    def test_get_db_name_env(self):
        projects = Projects(False)

        with mock.patch.dict("os.environ", {"DB3_PATH": "/path/"}):
            self.assertEqual("/path/statistics.db3", projects._get_db_name())

    def test_update_db_download_stats(self):
        PROJECT_NAME = "NAME"
        WORDS = 102

        projects = Projects(False)

        project_dao = ProjectMetaDataDao()
        project_dao.open(":memory:")
        projects.metadata_dao = project_dao

        project = MagicMock()
        project.get_words_entries = Mock(return_value=(WORDS, 20))
        project.name = PROJECT_NAME
        project.checksum = 0
        projects.add(project)
        projects._update_db_download_stats()

        project_dto = project_dao.get(PROJECT_NAME)
        self.assertEqual(WORDS, project_dto.words)

    def test_finished_test_download_all_projects_single_thread(self):
        with mock.patch.dict("os.environ", {"SINGLE_THREAD_DOWNLOAD": "1"}):
            projects = Projects(False)
            project = MagicMock()

            project.do = Mock()
            projects.add(project)
            projects._download_all_projects()
            project.do.assert_called()


if __name__ == "__main__":
    unittest.main()
