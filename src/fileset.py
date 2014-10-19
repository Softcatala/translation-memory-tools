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

import logging
import os
import shutil

from findfiles import FindFiles
from pofile import POFile


class FileSet():

    temp_dir = './tmp'

    def __init__(self, project_name, name, url, filename):
        self.project_name = project_name
        self.name = name
        self.url = url
        self.filename = filename
        self.add_source = True
        self.excluded = []

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

            pofile.add_comment_to_all_entries(msg)
            pofile.calculate_localized_string_checksum(self.checksum)

    def _clean_up(self):
        backup = 'tm-project-previous.po'
        shutil.copy(self.tm_file, backup)
        cmd = 'msgattrib {0} --no-fuzzy --no-obsolete --translated > {1}' \
              ' 2> /dev/null'
        os.system(cmd.format(backup, self.tm_file))
        os.remove(backup)

    def convert_ts_files_to_po(self):
        findFiles = FindFiles()

        for tsfile in findFiles.find(self.temp_dir, '*.ts'):
            fileName, fileExtension = os.path.splitext(tsfile)
            logging.info('convert ts file: {0}'.format(fileName))
            os.system('ts2po {0} -o {1}.po'.format(tsfile, fileName))

    def convert_string_files_to_po(self):
        findFiles = FindFiles()

        for tsfile in findFiles.find(self.temp_dir, '*.strings'):
            dirName = os.path.dirname(tsfile)
            logging.info('convert strings file: {0}'.format(dirName))
            filename = '{0}/strings-ca.po'.format(dirName)
            # Allow process files with duplicated entries
            cmd = 'prop2po -t {0}/en.strings {0}/ca.strings ' \
                '--personality strings --duplicates merge -o {1}'
            os.system(cmd.format(dirName, filename))

    def convert_ini_files_to_po(self):
        findFiles = FindFiles()

        for inifile in findFiles.find(self.temp_dir, 'ca.ini'):
            dirName = os.path.dirname(inifile)
            logging.info('convert ini file: {0}'.format(inifile))

            # http://bugs.locamotion.org/show_bug.cgi?id=3148
            # The rename operations can be removed when the issue is fixed
            os.rename('{0}/en.ini'.format(dirName),
                      '{0}/en.strings'.format(dirName))

            os.rename('{0}/ca.ini'.format(dirName),
                      '{0}/ca.strings'.format(dirName))

            filename = '{0}/strings-ca.po'.format(dirName)
            cmd = 'prop2po -t {0}/en.strings {0}/ca.strings --encoding=utf-8 ' \
                '--personality=strings -o {1}'
            os.system(cmd.format(dirName, filename))

    def _should_exclude_file(self, filename):
        exclude = False
        for exfilename in self.excluded:
            if filename.find(exfilename) != -1:
                exclude = True

        if exclude:
            logging.info('Excluding file: {0}'.format(filename))

        return exclude

    def build(self):
        findFiles = FindFiles()
        localtm = 'tm-local.po'

        files = findFiles.find(self.temp_dir, '*.po')

        if len(files) == 0:
            logging.info('No files to add in fileset: {0}'. format(self.name))
            return

        if os.path.isfile(localtm):
            os.remove(localtm)

        # Build using a local memory translation file
        for filename in files:

            if self._should_exclude_file(filename):
                continue

            msg = 'Adding file: {0} to translation memory'
            logging.info(msg.format(filename))

            if os.path.isfile(localtm):
                backup = 'tm-project-previous.po'
                shutil.copy(localtm, backup)
                cmd = 'msgcat -tutf-8 --use-first -o {0} {1} {2} 2> /dev/null'
                os.system(cmd.format(localtm, backup, filename))
                os.remove(backup)
            else:
                shutil.copy(filename, localtm)

        # Add to the project TM
        if os.path.isfile(self.tm_file):
            backup = 'tm-project-previous.po'
            shutil.copy(self.tm_file, backup)
            cmd = 'msgcat -tutf-8 --use-first -o {0} {1} {2} 2> /dev/null'
            os.system(cmd.format(self.tm_file, backup, localtm))
            os.remove(backup)
        else:
            shutil.copy(localtm, self.tm_file)

        if os.path.exists(localtm):
            os.remove(localtm)
        self._clean_up()

    def create_tmp_directory(self):
        self.remove_tmp_directory()
        os.makedirs(self.temp_dir)

    def remove_tmp_directory(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
