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

from project import *
from fileset import *

class Projects:

    def __init__(self, filename):
        self.filename = filename
        self.tmfile = "tm.po"
        self.projects = list()
        self.tm_project = Project('Translation memory', self.tmfile)
        
        if (os.path.isfile(filename)):
            os.system("rm " + filename)

    def Add(self, project):
        self.projects.append(project)


    def AddProject(self, project_dto, addSource):

        project = Project(project_dto.name, project_dto.filename)
        project.SetAddSource(addSource)
        project.AddFileSets(project_dto)
        self.Add(project)
        logging.debug(project_dto)

    def Do(self):

        for project in self.projects:
            project.Do()

        for project in self.projects:

            if (os.path.isfile(self.tmfile)):
                os.system("cp " + self.tmfile +" tm-previous.po")
                os.system("msgcat -tutf-8 --use-first -o " + self.tmfile + " tm-previous.po " + project.GetFilename())
                os.system("rm -f tm-previous.po")
            else:
                os.system("cp " + project.GetFilename() + " " + self.tmfile)

        os.system("msgfmt -c --statistics " + self.tmfile)

    def Statistics(self):
        
        for project in self.projects:
            project.Statistics()

        self.tm_project.Statistics()

    def ToTmx(self):
        
        for project in self.projects:
            project.ToTmx()

        self.tm_project.ToTmx()



