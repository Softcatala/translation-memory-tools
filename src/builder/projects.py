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
from concurrent.futures import ProcessPoolExecutor

from .project import Project
from .projectmetadatadao import ProjectMetaDataDao
from .projectmetadatadto import ProjectMetaDataDto
from .pocatalog import POCatalog
from .licenses import Licenses

class Projects(object):

    ENV_NAME = 'DB3_PATH'

    def __init__(self, opendb = True):
        self.projects = list()
        self.out_directory = ""
        self.set_tm_file('tots-tm.po')
        self.metadata_dao = ProjectMetaDataDao()

        if opendb:
            self.metadata_dao.open(self._get_db_name())

    def _get_db_name(self):
        name = 'statistics.db3'

        if self.ENV_NAME not in os.environ:
            return name

        path = os.environ[self.ENV_NAME]
        return os.path.join(path, name)

    def set_tm_file(self, filename):
        self.tm_file = filename
        name = 'Translation memory'
        self.tm_project = Project(name, name, self.tm_file)
        self.tm_project.set_out_directory(self.out_directory)

    def set_out_directory(self, out_directory):
        self.out_directory = out_directory
        self.tm_project.set_out_directory(out_directory)

    def add(self, project):
        self.projects.append(project)

    def add_project(self, project_dto, add_source):
        project = Project(project_dto.name, project_dto.project_id, project_dto.filename)
        project.license = project_dto.license
        project.set_add_source(add_source)
        project.set_out_directory(self.out_directory)
        project.add_filesets(project_dto)
        self.add(project)
        logging.debug(project_dto)

    def __call__(self):
        """Process all projects"""

        # We use Processess instead of Theads because some filesets (e.g. transifex) need to
        # to change the proccess directory to work.
        # The number of processess to use is calculated by Python taking into account number of cpus
        project_futures = {}
        with ProcessPoolExecutor() as executor:
            for project in self.projects:
                future = executor.submit(project.do)
                project_futures[project] = future

        # executor.submit copies the object and runs it in another process.
        # The project object in this thread does not get updated then we need
        # to update our object here.
        for project, feature in project_futures.items():
            try:
                project.checksum = feature.result()
            except:
                logging.error(f"Projects.__call__. Feature.result() error on '{project.name}' project")

        for project in self.projects:

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

        COMBINED_LICENSE = 'GPL-3.0-only'

        tm_file = os.path.join(self.out_directory, self.tm_file)
        if os.path.isfile(tm_file):
            os.remove(tm_file)

        projects_catalog = POCatalog(tm_file)

        total_words = 0
        included_prjs = 0
        skipped_prjs = 0
        skipped_words = 0
        for project in self.projects:
            license = project.license.lower()
            if project.license.lower() == Licenses().PROPIETARY:
                logging.debug(f"Projects. Skipping {project.name} into {self.tm_file} memory")
                continue

            words, _ = project.get_words_entries()

            if Licenses().are_compatible_licenses(COMBINED_LICENSE, project.license) is False:
                skipped_words += words
                skipped_prjs += 1
                continue

            total_words += words
            included_prjs += 1
            project_catalog = POCatalog(project.get_filename_fullpath())
            projects_catalog.add_pofile(project_catalog.filename)

        projects_catalog.cleanup()
        logging.info(f"Projects. Added into {self.tm_file} a total of {total_words} words from {included_prjs} "\
                    f"projects. Skipped {skipped_prjs} project(s) with {skipped_words} words due to license incompatibility")

    def statistics(self):
        for project in self.projects:
            project.statistics()

        words, entries = self.tm_project.get_words_entries()
        if words > 0:
            logging.info(f'Translation memory for all projects: {entries} translated strings, words {words}')
        else:
            logging.info('Translation memory for all projects is empty. No projects were added.')

        self.metadata_dao.close()

    def to_tmx(self):
        for project in self.projects:
            project.to_tmx()

        self.tm_project.to_tmx()
