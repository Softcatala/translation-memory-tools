# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Jordi Mas i Hernandez <jmas@softcatala.org>
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
from .downloadfile import DownloadFile
from .fileset import FileSet
from .filefileset import FileFileSet


class PontoonFileSet(FileSet):
    """
        Reads a list of projects from a Pontoon server by calling
        their API and then downloads the projects.
    """

    def set_project(self, project):
        self.project = project

    def do(self):
        # Download JSON file
        url = self.url + 'graphql?query={locale(code:"ca"){name,localizations{project{name,slug}}}}'
        download = DownloadFile()
        download.get_file(url, self.filename)

        # The Pontoon project has a single fileset assigned (this)
        # We empty the fileset and add dynamically the ones referenced by Gerrit
        self.project.filesets = []

        with open(self.filename) as json_data:
            data = json.load(json_data)

            # Get every project entry
            #print(data['data']['locale'])
            for value in data['data']['locale']['localizations']:
                value = value['project']
                name = None
                slug = None

                for prj_attribute, prj_value in value.items():
                    if prj_attribute == 'name':
                        name = prj_value
                    elif prj_attribute == 'slug':
                        slug = prj_value

                url = self.url + 'ca/{0}/ca.tmx'.format(slug)
                fileset = FileFileSet(self.project_name, name, url, slug + '.tmx', self)

                logging.debug("PontoonFileSet. Adding {0}-{1}".format(self.project_name, name))
                self.project.add_fileset(fileset)

        # All the new filesets have been added re-process project now
        logging.info('PontoonFileSet. Added {0} filesets dynamically'.
                      format(len(self.project.filesets)))

        self.project.report_errors = False
        self.project.do()
