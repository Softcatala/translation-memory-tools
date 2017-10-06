# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import datetime
import logging
import os

from .project import Project
from .projectmetadatadao import ProjectMetaDataDao
from .projectmetadatadto import ProjectMetaDataDto
from .pocatalog import POCatalog


class Projects(object):

    def __init__(self):
        self.projects = list()
        self.out_directory = ""
        self.set_tm_file('tots-tm.po')
        self.metadata_dao = ProjectMetaDataDao()
        self.metadata_dao.open('statistics.db3')

    def set_tm_file(self, filename):
        self.tm_file = filename
        self.tm_project = Project('Translation memory', self.tm_file)
        self.tm_project.set_out_directory(self.out_directory)

    def set_out_directory(self, out_directory):
        self.out_directory = out_directory
        self.tm_project.set_out_directory(out_directory)

    def add(self, project):
        self.projects.append(project)

    def add_project(self, project_dto, add_source):
        project = Project(project_dto.name, project_dto.filename)
        project.set_add_source(add_source)
        project.set_out_directory(self.out_directory)
        project.add_filesets(project_dto)
        self.add(project)
        logging.debug(project_dto)

    def __call__(self):
        """Process all projects"""
        for project in self.projects:
            project.do()

            words, entries = project.get_words_entries()

            if words == -1:
                continue

            metadata_dto = self.metadata_dao.get(project.name)
            if metadata_dto is None:
                metadata_dto = ProjectMetaDataDto(project.name)

            if (metadata_dto.checksum is None or
                metadata_dto.checksum != project.checksum):
                metadata_dto.last_translation_update = datetime.datetime.now()
                metadata_dto.checksum = project.checksum

            metadata_dto.last_fetch = datetime.datetime.now()
            metadata_dto.words = words
            self.metadata_dao.put(metadata_dto)

        self.create_tm_for_all_projects()

        DAYS_TO_KEEP = 90
        result = self.metadata_dao.delete_last_fetch(DAYS_TO_KEEP)
        logging.info("Projects clean up:" + str(result))

    def create_tm_for_all_projects(self):
        """Creates the TM memory for all projects"""

        tm_file = os.path.join(self.out_directory, self.tm_file)
        if os.path.isfile(tm_file):
            os.remove(tm_file)

        projects_catalog = POCatalog(tm_file)

        for project in self.projects:
            project_catalog = POCatalog(project.get_filename_fullpath())
            projects_catalog.add_pofile(project_catalog.filename)

        projects_catalog.cleanup()

    def statistics(self):
        for project in self.projects:
            project.statistics()

        self.tm_project.statistics()
        self.metadata_dao.close()

    def to_tmx(self):
        for project in self.projects:
            project.to_tmx()

        self.tm_project.to_tmx()
