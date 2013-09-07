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

import json
from collections import OrderedDict


class ProjectDTO:

    def __init__(self):
        self.name = ""
        self.filename = ""
        self.filesets = list()
        return

    def __str__(self):
        return "ProjectDTO. Name: " + self.name + ", filename:" + self.filename


class FileSetDTO:

    def __init__(self):
        self.name = ""
        self.url = ""
        self.type = ""
        self.excluded = ""
        self.target = ""
        return

    def __str__(self):
        return  "FileSetDTO. Name: " + self.name + ", url:" + self.url + ", type:" + self.type + ", excluded:" + self.excluded +  ", target:" + self.target


class JsonBackend:

    def __init__(self, filename):
        self.filename = filename
        self.projects = list()
        return

    def _processFileSet(self, project, project_value):

        for fileset_attr, fileset_value in project_value.iteritems():
            fileset = FileSetDTO()
            project.filesets.append(fileset)
            fileset.name = fileset_attr

            self._processFileSetAttributes(fileset, fileset_value)

    def _processFileSetAttributes(self, fileset, fileset_value):

        for fileset_properties_attr, fileset_properties_value in fileset_value.iteritems():
            if (fileset_properties_attr == 'name'):
                fileset.name = fileset_properties_value
            elif (fileset_properties_attr == 'url'):
                fileset.url = fileset_properties_value
            elif (fileset_properties_attr == 'type'):
                fileset.type = fileset_properties_value
            elif (fileset_properties_attr == 'target'):
                fileset.target = fileset_properties_value
            elif (fileset_properties_attr == 'excluded'):
                fileset.excluded = fileset_properties_value

    def load(self):

        json_data = open(self.filename)
        data = json.load(json_data, object_pairs_hook=OrderedDict)

        # Enums projects names
        for attribute, value in data['projects'].items():
            project = ProjectDTO()
            project.name = attribute
            self.projects.append(project)

            #Enum project sets
            for project_attr, project_value in value.iteritems():
                if (project_attr == 'filename'):
                    project.filename = project_value
                elif (project_attr == 'fileset'):
                    self._processFileSet(project, project_value)

        json_data.close()
