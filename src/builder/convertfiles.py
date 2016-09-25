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
import shutil

from .findfiles import FindFiles


class ConvertFiles():

    def __init__(self, convert_dir, conversor_setup):
        self.convert_dir = convert_dir
        self.findFiles = None
        self.conversor_setup = conversor_setup
        self.android_dir = None

    def convert(self):
        self.findFiles = FindFiles()
        self._convert_ts_files_to_po()
        self._convert_string_files_to_po()
        self._convert_ini_files_to_po()
        self._convert_php_resources_files_to_po()
        self._convert_android_resources_files_to_po()
        self._convert_properties_files_to_po()
        self._convert_json_files_to_po()
        self._convert_yml_files_to_po()

    def _convert_ts_files_to_po(self):
        for tsfile in self.findFiles.find(self.convert_dir, '*.ts'):
            fileName, fileExtension = os.path.splitext(tsfile)
            logging.info('convert ts file: {0}'.format(tsfile))
            os.system('ts2po {0} -o {1}.po'.format(tsfile, fileName))

    def _convert_string_files_to_po(self):
        for tsfile in self.findFiles.find(self.convert_dir, 'ca.strings'):
            dirName = os.path.dirname(tsfile)
            logging.info('convert strings file: {0}'.format(dirName))
            filename = '{0}/strings-ca.po'.format(dirName)
            # Allow process files with duplicated entries
            cmd = 'prop2po -t {0}/en.strings {0}/ca.strings ' \
                '--personality strings --duplicates merge -o {1}'
            os.system(cmd.format(dirName, filename))

    def _convert_properties_files_to_po(self):
        for tsfile in self.findFiles.find(self.convert_dir, 'ca.properties'):
            dirName = os.path.dirname(tsfile)
            logging.info('convert properties file: {0}'.format(dirName))
            filename = '{0}/properties-ca.po'.format(dirName)
            # Allow process files with duplicated entries
            cmd = 'prop2po -t {0}/en.properties {0}/ca.properties ' \
                '--personality java --duplicates merge -o {1}'

            if self.conversor_setup is not None and \
               self.conversor_setup.type == 'string' and \
               self.conversor_setup.verb == 'add':
                cmd += self.conversor_setup.command
                logging.info('Adding parameter to conversor: {0}'.
                             format(self.conversor_setup.command))

            os.system(cmd.format(dirName, filename))

    def _execute_convert_ini_files_to_po(self, src, trg, dirName):
        os.rename(src, '{0}/en.strings'.format(dirName))
        os.rename(trg, '{0}/ca.strings'.format(dirName))

        filename = '{0}/strings-ca.po'.format(dirName)
        cmd = 'prop2po -t {0}/en.strings {0}/ca.strings --encoding=utf-8 '\
            '--personality=strings -o {1}'
        os.system(cmd.format(dirName, filename))

    def _convert_ini_files_to_po(self):
        for inifile in self.findFiles.find(self.convert_dir, 'ca*.ini'):
            dirName = os.path.dirname(inifile)
            logging.info('convert ini file: {0}'.format(inifile))

            # http://bugs.locamotion.org/show_bug.cgi?id=3148
            # The rename operations can be removed when the issue is fixed

            src = None
            filename = '{0}/en.ini'.format(dirName)
            if os.path.isfile(filename):
                src = filename
            else:
                filename = '{0}/en_GB.ini'.format(dirName)
                if os.path.isfile(filename):
                    src = filename

            trg = None
            filename = '{0}/ca.ini'.format(dirName)
            if os.path.isfile(filename):
                trg = filename
            else:
                filename = '{0}/ca_ES.ini'.format(dirName)
                if os.path.isfile(filename):
                    trg = filename

            if src is not None and trg is not None:
                self._execute_convert_ini_files_to_po(src, trg, dirName)

    def _convert_php_resources_files_to_po(self):
        if len(self.findFiles.find(self.convert_dir, '*.php')) == 0:
            return

        logging.info('convert php directory: {0}'.format(self.convert_dir))
        # Name arbitrary choosen (not sepecific to an expected dir structure)
        OUT_DIRNAME = 'po-files'
        cmd = 'cd {0} && php2po -t en -i ca ' \
              '-o {1}'.format(self.convert_dir, OUT_DIRNAME)
        os.system(cmd)

    '''
        OpenWhisperSystems conditional conversion code for Android
        To be refactor when patterns for Android dir structure is clear, 
        including Xiaomi
    '''
    def _process_ows_projects(self):
        ca_file = os.path.join(self.convert_dir, 
                               "translations/signal-android.master/ca.xml")

        en_file = os.path.join(self.convert_dir, 
                               "translations/signal-android.master/en.xml")

        if os.path.isfile(ca_file) == False or os.path.isfile(en_file) == False:
            ca_file = os.path.join(self.convert_dir, 
                                   "translations/redphone.master/ca.xml")

            en_file = os.path.join(self.convert_dir, 
                                   "translations/redphone.master/en.xml")

            if os.path.isfile(ca_file) == False or os.path.isfile(en_file) == False:
                return

        directory = os.path.join(self.convert_dir, 'signal')
        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = os.path.join(self.convert_dir,'signal/res')
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        directory = os.path.join(self.convert_dir,'signal/res/values-ca')
        if not os.path.exists(directory):
            os.makedirs(directory)
                
        shutil.copy2(ca_file, os.path.join(directory, "strings.xml"))

        directory = os.path.join(self.convert_dir,'signal/res/values')
        if not os.path.exists(directory):
            os.makedirs(directory)
                
        shutil.copy2(en_file, os.path.join(directory, "strings.xml"))
        self.android_dir = 'signal/res'


    def _convert_android_resources_files_to_po(self):
        if len(self.findFiles.find(self.convert_dir, '*.xml')) == 0:
            return

        logging.info('convert Android directory: {0}'.format(self.convert_dir))
        # See: https://pypi.python.org/pypi/android2po/1.2.0
        # If you do not specify --gettext ., the file is writen in ../locale
        # outside the tmp directory in our case
        cmd = 'cd {0} && a2po init ca --gettext .'.format(self.convert_dir)

        self._process_ows_projects()

        if self.android_dir is not None:
            cmd += " --android {0}".format(self.android_dir)

        os.system(cmd)

    def _convert_json_files_to_po(self):
        for jsonfile in self.findFiles.find(self.convert_dir, 'ca.json'):
            dirName = os.path.dirname(jsonfile)
            logging.info('convert json file: {0}'.format(dirName))
            filename = '{0}/json-ca.po'.format(dirName)
            cmd = 'json2po -t {0}/en.json -i {0}/ca.json ' \
                  '-o {1}'.format(dirName, filename)
            os.system(cmd)

    def _convert_yml_files_to_po(self):
        for ymlfile in self.findFiles.find(self.convert_dir, 'ca.yml'):
            dirName = os.path.dirname(ymlfile)
            logging.info('convert yml file: {0}'.format(dirName))
            cmd = 'i18n-translate convert --locale_dir {0} -f yml -l ca -t po -d en'.format(dirName)
            os.system(cmd)
