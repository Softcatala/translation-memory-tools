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

import json
import logging
from collections import OrderedDict
from findfiles import FindFiles

class ProjectDTO(object):

    def __init__(self, name):
        self.name = name
        self.filename = ''
        self.projectweb = ''
        self.softcatala = False
        self.disabled = False
        self.downloadable = True
        self.selectable = True
        self.filesets = []

    def __str__(self):
        text = ('ProjectDTO. Name: {0}, filename: {1}, project web: {2}, '
                'disabled {3}, softcatala {4}')
        return text.format(self.name, self.filename, self.projectweb,
                           self.disabled, self.softcatala)


class FileSetDTO(object):

    def __init__(self):
        self.name = ''
        self.url = ''
        self.type = ''
        self.excluded = ''
        self.target = ''
        self.pattern = ''

    def __str__(self):
        text = ('FileSetDTO. Name: {0}, url: {1}, type: {2}, excluded: {3}, '
                'target: {4}, pattern: {5}')
        return text.format(self.name, self.url, self.type, self.excluded,
                           self.target, self.pattern)


class JsonBackend(object):

    def __init__(self, directory):
        self.directory = directory
        self.projects = []

    def _process_fileset(self, project, project_value):
        for fileset_attr, fileset_value in project_value.iteritems():
            fileset = FileSetDTO()
            project.filesets.append(fileset)
            fileset.name = fileset_attr

            self._process_file_set_attributes(fileset, fileset_value)

    def _process_file_set_attributes(self, fileset, fileset_value):
        for fileset_properties_attr, fileset_properties_value in \
                fileset_value.iteritems():
            if fileset_properties_attr == 'name':
                fileset.name = fileset_properties_value
            elif fileset_properties_attr == 'url':
                fileset.url = fileset_properties_value
            elif fileset_properties_attr == 'type':
                fileset.type = fileset_properties_value
            elif fileset_properties_attr == 'target':
                fileset.target = fileset_properties_value
            elif fileset_properties_attr == 'excluded':
                fileset.excluded = fileset_properties_value
            elif fileset_properties_attr == 'pattern':
                fileset.pattern = fileset_properties_value
            else:
                msg = "Field '{0}' not recognized"
                logging.error(msg.format(fileset_properties_attr))

    def load(self):

        findFiles = FindFiles()

        for filename in findFiles.find(self.directory, '*.json'):
            self._load_file(filename)

    def _load_file(self, filename):
        with open(filename) as json_data:
            data = json.load(json_data, object_pairs_hook=OrderedDict)

            # Parse projects
            project = ProjectDTO(data['project'])
            for attribute, value in data.items():

                if attribute in ('filename', 'projectweb', 'softcatala', 'disabled',
                             'downloadable', 'selectable'):
                    setattr(project, attribute, data[attribute])


                if 'fileset' in attribute:
                    self._process_fileset(project, data['fileset'])

            if project.disabled is False:
                project.filename = '{0}-tm.po'.format(project.name.lower())
                self.projects.append(project)
