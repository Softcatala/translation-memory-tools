#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import sys
sys.path.append('../src/')
import os
import shutil
import tempfile
import urllib
import urllib2

from jsonbackend import JsonBackend
from findfiles import FindFiles


class CheckDownloads(object):

    HTTP_STATUS_CODE_OK = 200
    HTTP_STATUS_CODE_NOT_FOUND = 404

    def __init__(self, links):
        self.links = links
        self.temp_dir = './tmp'
        self.errors = 0

    def _get_link_from_filename(self, filename):
        for link in self.links:
            pos = link.find(filename)
            if pos != -1:
                return link

        return None

    def is_filename_a_download(self, filename):
        found = False

        link = self._get_link_from_filename(filename)
        if link is not None:
            code = CheckDownloads.HTTP_STATUS_CODE_NOT_FOUND
            try:
                rtr = urllib2.urlopen(link)
                code = rtr.getcode()
            except Exception:
                pass

            if code != CheckDownloads.HTTP_STATUS_CODE_OK:
                print('link {0} returns {1}'.format(link, str(code)))
            else:
                found = True

        if not found:
            self.errors += 1
            print('Missing link {0}'.format(filename))

        return found

    def _create_tmp_directory(self):
        self._remove_tmp_directory()
        os.makedirs(self.temp_dir)

    def _remove_tmp_directory(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def check_zipfile(self,
                      filename,
                      extensions,
                      expected_files,
                      minimum_size):
        tmp_file = tempfile.NamedTemporaryFile()
        link = self._get_link_from_filename(filename)

        if link is None:
            return

        urllib.urlretrieve(link, tmp_file.name)

        self._create_tmp_directory()

        cmd = 'unzip {0} -d {1} > /dev/null'.format(
            tmp_file.name,
            self.temp_dir
        )
        os.system(cmd)

        files = 0
        findFiles = FindFiles()
        for filename in findFiles.find(self.temp_dir, extensions):
            files = files + 1

            size = os.path.getsize(filename)
            if size < minimum_size:
                self.errors += 1
                print('File {0} has size {1} but expected was at least {2}'. \
                      format(filename, size, minimum_size))

        if files != expected_files:
            self.errors += 1
            print('{0} expected {1} files but contains {2}'.format(link,
                  expected_files, files))

        self._remove_tmp_directory()

    def downloads_for_project(self, name, expected_files):
        print("Processing:" + name)

        # Po files
        MIN_PO_SIZE = 1500
        po_zip_file = '{0}-tm.po.zip'.format(name.lower())
        if self.is_filename_a_download(po_zip_file):
            self.check_zipfile(po_zip_file,
                               '*.po',
                               expected_files,
                               MIN_PO_SIZE)

        # Tmx files
        MIN_TMX_SIZE = 350
        tmx_zip_file = '{0}-tm.tmx.zip'.format(name.lower())
        if self.is_filename_a_download(tmx_zip_file):
            self.check_zipfile(tmx_zip_file, '*.tmx', expected_files,
                               MIN_TMX_SIZE)

    def check_project_link(self, project_web):
        if project_web is None or len(project_web) == 0:
            return

        code = CheckDownloads.HTTP_STATUS_CODE_NOT_FOUND
        try:
            rtr = urllib2.urlopen(project_web)
            code = rtr.getcode()
        except Exception:
            pass

        if code != CheckDownloads.HTTP_STATUS_CODE_OK:
            print('Project link {0} returns {1}'.format(project_web,
                                                        str(code)))
            return False
        else:
            return True

    def check(self):
        """Reads the json and makes sure that for every project we have a
        po and a tmx that is a download published with the expected files
        """
        json = JsonBackend("../src/projects.json")
        json.load()

        TM_ITSELF = 1
        expected_files = TM_ITSELF + sum(p.downloadable is True
                                         for p in json.projects)
        self.downloads_for_project('tots', expected_files)

        expected_files = TM_ITSELF + sum(p.softcatala is True and
                                         p.downloadable is True
                                         for p in json.projects)

        self.downloads_for_project('softcatala', expected_files)

        expected_files = 1
        for project_dto in json.projects:
            if not project_dto.downloadable:
                continue

            self.downloads_for_project(project_dto.name, expected_files)
            self.check_project_link(project_dto.projectweb)
