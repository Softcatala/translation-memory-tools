# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Jordi Mas i Hernandez <jmas@softcatala.org>
# Copyright (c) 2014 Leandro Regueiro Iglesias <leandro.regueiro@gmail.com>
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
import os
import shutil

from .downloadfile import DownloadFile
from .fileset import FileSet
from .gitfileset import GitFileSet


class GerritDirectoryFileSet(FileSet):
    """
    Reads a list of projects from a Gerrit (Git web) server by calling
    their API and then downloads the projects.
    """

    def set_project(self, project):
        self.project = project

    def _remove_first_line_from_file(self, filename):
        """Garbage prefix inserted before JSON output to prevent XSSI.

        This prefix is ")]}'\n" and is designed to prevent a web browser from
        executing the response body.
        """
        working_file = filename + ".old"
        shutil.copy(filename, working_file)

        with open(working_file, "r") as reader, open(filename, "w") as writter:
            lines = reader.readlines()

            cnt = 0
            for line in lines:
                cnt += 1
                if cnt == 1:
                    continue

                writter.write(line)

        os.remove(working_file)

    def expand_dynamic(self):
        # Download JSON file
        download = DownloadFile()
        download.get_file(self.url, self.filename)

        self._remove_first_line_from_file(self.filename)

        # The Gerrit project has a single fileset assigned (this)
        # We empty the fileset and add dynamically the ones referenced by Gerrit
        self.project.filesets = []

        with open(self.filename) as json_data:
            data = json.load(json_data)

            # Get every project entry
            for attribute, value in data.items():
                name = None
                url = None
                for prj_attribute, prj_value in value.items():
                    if prj_attribute == "name":
                        name = prj_value
                    elif prj_attribute == "clone_url":
                        url = prj_value

                if not self.is_retrieval_pattern(name):
                    logging.debug("GerritDirectoryFileSet. Discarding:" + name)
                    continue

                fileset = GitFileSet(self.project_name, self.project_id, name, url, "")

                # Some Android projects contain there own po files like
                # https://android.googlesource.com/platform/ndk and they have
                # the name standard "ca.po"
                # The rest are produced by android2po then they have the pattern '-ca.po'
                fileset.set_pattern(r".*?ca\.po")
                logging.debug("Gerrit adding {0}-{1}".format(self.project_name, name))
                self.project.add_fileset(fileset)

        # All the new filesets have been added re-process project now
        logging.info(
            "GerritDirectoryFileSet. Added {0} filesets dynamically".format(
                len(self.project.filesets)
            )
        )
        self.project.report_errors = False
        os.remove(self.filename)
