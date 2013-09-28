#!/usr/bin/python2
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


import os
import logging

from project import Project


class Projects:

    def __init__(self, filename):
        self.filename = filename
        self.tm_file = "tm.po"
        self.projects = list()
        self.tm_project = Project('Translation memory', self.tm_file)

        if (os.path.isfile(filename)):
            os.system("rm " + filename)

    def add(self, project):
        self.projects.append(project)

    def add_project(self, project_dto, add_source):

        project = Project(project_dto.name, project_dto.filename)
        project.set_add_source(add_source)
        project.add_filesets(project_dto)
        self.add(project)
        logging.debug(project_dto)

    def do(self):
        '''Proces all projects''' 
        for project in self.projects:
            project.do()
            
        self.create_tm_for_all_projects()
        
    def create_tm_for_all_projects(self):
        '''Creates the TM memory for all projects''' 
        for project in self.projects:

            if (os.path.isfile(self.tm_file)):
                os.system("cp " + self.tm_file + " tm-previous.po")
                os.system("msgcat -tutf-8 --use-first -o " + self.tm_file
                          + " tm-previous.po " + project.get_filename())
                os.system("rm -f tm-previous.po")
            else:
                os.system("cp " + project.get_filename() + " " + self.tm_file)

        os.system("msgfmt -c --statistics " + self.tm_file)

    def statistics(self):

        for project in self.projects:
            project.statistics()

        self.tm_project.statistics()

    def to_tmx(self):

        for project in self.projects:
            project.to_tmx()

        self.tm_project.to_tmx()
