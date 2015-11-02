# -*- coding: utf-8 -*-
#
# Copyright (c) 2012-2014 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import logging
import os
import shutil

from convertfiles import ConvertFiles
from findfiles import FindFiles
from pocatalog import POCatalog
from pofile import POFile


class FileSet():

    temp_dir = './tmp'
    output_dir = './output'

    def __init__(self, project_name, name, url, filename):
        self.project_name = project_name
        self.name = name
        self.url = url
        self.filename = filename
        self.add_source = True
        self.excluded = []
        self.po_catalog = None
        self.output_dir = self.output_dir + "/" + project_name.lower() + "/" + name.lower()
        self.words = -1

    def set_checksum(self, checksum):
        self.checksum = checksum

    def set_add_source(self, add_source):
        self.add_source = add_source

    def set_tm_file(self, tm_file):
        self.tm_file = tm_file

    def add_excluded(self, filename):
        if len(filename) > 0:
            self.excluded.append(filename)

    def add_comments(self):
        if not self.add_source:
            return

        findFiles = FindFiles()

        for filename in findFiles.find(self.temp_dir, '*.po'):
            relative = filename.replace(self.temp_dir, '')
            pofile = POFile(filename)

            if self.project_name.lower().strip() == self.name.lower().strip():
                msg = 'Source: {0} from project \'{1}\'' \
                    .format(relative, self.project_name)
            else:
                msg = 'Source: {0} from project \'{1} - {2}\'' \
                    .format(relative, self.project_name, self.name)

            self.words += pofile.get_statistics()

            pofile.add_comment_to_all_entries(msg)
            pofile.calculate_localized_string_checksum(self.checksum)

    def _should_exclude_file(self, filename):
        exclude = False
        for exfilename in self.excluded:
            if filename.find(exfilename) != -1:
                exclude = True

        if exclude:
            logging.info('Excluding file: {0}'.format(filename))

        return exclude

    def clean_up_after_convert(self):
        pass

    def _delete_tm_fileset(self, fileset_tm):
        if os.path.isfile(fileset_tm):
            os.remove(fileset_tm)

    def _build_tm_for_fileset(self, fileset_tm, files):
        for filename in files:

            if self._should_exclude_file(filename):
                continue

            msg = 'Adding file: {0} to translation memory'
            logging.info(msg.format(filename))
            self.po_catalog.add_pofile(filename)

    def _add_tm_for_fileset_to_project_tm(self, fileset_tm):
        project_catalog = POCatalog(self.tm_file)
        project_catalog.add_pofile(self.po_catalog.filename)
        project_catalog.cleanup()

    def do_withtemp(self):
        self._create_tmp_directory()
        self.do()
        self._remove_tmp_directory()
        
    def build(self):
        convert = ConvertFiles(self.temp_dir)
        convert.convert()

        self.clean_up_after_convert()
        self.add_comments()

        findFiles = FindFiles()
        files = findFiles.find(self.temp_dir, '*.po')

        if len(files) == 0:
            logging.info('No files to add in fileset: {0}'. format(self.name))
            return

        fileset_tm = 'fileset-tm.po'
        self.po_catalog = POCatalog(fileset_tm)
        self._build_tm_for_fileset(fileset_tm, files)
        self._add_tm_for_fileset_to_project_tm(fileset_tm)
        self._delete_tm_fileset(fileset_tm)
        self._copy_to_output()

    def _copy_to_output(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        findFiles = FindFiles()
        files = findFiles.find(self.temp_dir, '*.po')
        for source in files:
            dirname = os.path.dirname(source)
            if dirname != self.temp_dir:
                d = self.output_dir + dirname[len(self.temp_dir):]
                if not os.path.exists(d):
                    os.makedirs(d)

            target = self.output_dir + source[len(self.temp_dir):]
            shutil.copy(source, target)

    def _create_tmp_directory(self):
        self._remove_tmp_directory()
        os.makedirs(self.temp_dir)

    def _remove_tmp_directory(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
