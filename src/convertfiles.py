# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from findfiles import FindFiles


class ConvertFiles():

    temp_dir = './tmp'

    def convert(self):
        self._convert_ts_files_to_po()
        self._convert_string_files_to_po()
        self._convert_ini_files_to_po()
        self._php_conversion_for_moodle()
        self._convert_android_resources_files_to_po()
        self. _convert_properties_files_to_po()

    def _convert_ts_files_to_po(self):
        findFiles = FindFiles()

        for tsfile in findFiles.find(self.temp_dir, '*.ts'):
            fileName, fileExtension = os.path.splitext(tsfile)
            logging.info('convert ts file: {0}'.format(fileName))
            os.system('ts2po {0} -o {1}.po'.format(tsfile, fileName))

    def _convert_string_files_to_po(self):
        findFiles = FindFiles()

        for tsfile in findFiles.find(self.temp_dir, '*.strings'):
            dirName = os.path.dirname(tsfile)
            logging.info('convert strings file: {0}'.format(dirName))
            filename = '{0}/strings-ca.po'.format(dirName)
            # Allow process files with duplicated entries
            cmd = 'prop2po -t {0}/en.strings {0}/ca.strings ' \
                '--personality strings --duplicates merge -o {1}'
            os.system(cmd.format(dirName, filename))

    def _convert_properties_files_to_po(self):
        findFiles = FindFiles()

        for tsfile in findFiles.find(self.temp_dir, '*.properties'):
            dirName = os.path.dirname(tsfile)
            logging.info('convert properties file: {0}'.format(dirName))
            filename = '{0}/properties-ca.po'.format(dirName)
            # Allow process files with duplicated entries
            cmd = 'prop2po -t {0}/en.properties {0}/ca.properties ' \
                '--personality java --duplicates merge -o {1}'
            os.system(cmd.format(dirName, filename))

    def _convert_ini_files_to_po(self):
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

    def _php_conversion_for_moodle(self):
        findFiles = FindFiles()
        if len(findFiles.find(self.temp_dir, '*.php')) == 0:
            return

        GIT_DIRNAME = 'moodle-langpacks'
        OUT_DIRNAME = 'po-files'
        cmd = 'cd {0} && php2po -t {1}/en -i {1}/ca ' \
              '-o {2}'.format(self.temp_dir, GIT_DIRNAME, OUT_DIRNAME)
        os.system(cmd)

    def _convert_android_resources_files_to_po(self):

        # See: https://pypi.python.org/pypi/android2po/1.2.0
        cmd = 'cd {0}/{1} && a2po init ca'.format(self.temp_dir, "ca.po")
        os.system(cmd)
