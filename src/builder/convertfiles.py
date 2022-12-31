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

from .converttmx import ConvertTmx
from .findfiles import FindFiles
from .convertini import ConvertIni

class ConvertFiles():

    def __init__(self, convert_dir, conversor_setup):
        self.convert_dir = convert_dir
        self.findFiles = None
        self.conversor_setup = conversor_setup
        self.android_dir = None

    def convert(self):
        self.findFiles = FindFiles()
        self._uncompress_files()
        self._convert_tmx_files_to_po()
        self._convert_ts_files_to_po()
        self._convert_string_files_to_po()
        self._convert_ini_files_to_po()
        self._convert_php_resources_files_to_po()
        self._convert_android_resources_files_to_po()
        self._convert_properties_files_to_po()
        self._convert_json_files_to_po()
        self._convert_yml_files_to_po()
        self._convert_csv_files_to_po()
        self._convert_xliff_file_to_po()

    def _convert_ts_files_to_po(self):
        for tsfile in self.findFiles.find_recursive(self.convert_dir, '*.ts'):
            fileName, fileExtension = os.path.splitext(tsfile)
            logging.info('convert ts file: {0}'.format(tsfile))
            os.system('ts2po {0} -o {1}.po'.format(tsfile, fileName))

    def _convert_string_files_to_po(self):
        for tsfile in self.findFiles.find_recursive(self.convert_dir, 'ca.strings'):
            dirName = os.path.dirname(tsfile)
            logging.info('convert strings file: {0}'.format(dirName))
            filename = '{0}/strings-ca.po'.format(dirName)
            # Allow process files with duplicated entries
            cmd = 'prop2po -t {0}/en.strings {0}/ca.strings ' \
                '--personality strings --duplicates merge -o {1}'
            os.system(cmd.format(dirName, filename))

    def _uncompress_files(self):
        for zipfile in self.findFiles.find_recursive(self.convert_dir, '*.zip'):
            # Some projects have files with passwords that we do not know,
            # we pass an 'unknown' password to prevent been prompted for it
            cmd = 'unzip -p unknown -t {0} > /dev/null '.format(zipfile)
            os.system(cmd)

    def _convert_tmx_files_to_po(self):
        for tmxfile in self.findFiles.find_recursive(self.convert_dir, '*.tmx'):
            fileName, fileExtension = os.path.splitext(tmxfile)
            tmx = ConvertTmx(tmxfile, fileName + ".po")
            tmx.convert()
            logging.info('convert tmx file: {0}'.format(tmxfile))

    def _convert_csv_files_to_po(self):
        for csvfile in self.findFiles.find_recursive(self.convert_dir, 'ca.csv'):
            dirName = os.path.dirname(csvfile)
            pofile = dirName + '/ca.po'
            cmd = 'csv2po -i {0} -o {1}'.format(csvfile, pofile)
            os.system(cmd)
            logging.info('convert csv file: {0}'.format(csvfile))

    def _convert_properties_files_to_po(self):
        files = self.findFiles.find_recursive(self.convert_dir, 'ca.properties')
        if len(files) == 0:
            files = self.findFiles.find_recursive(self.convert_dir, 'ca_ES.properties')

        for propfile in files:
            dirName = os.path.dirname(propfile)
            prop_filename = os.path.basename(propfile)
            logging.info('convert properties file: {0}'.format(dirName))
            po_filename = '{0}/properties-ca.po'.format(dirName)
            # Allow process files with duplicated entries
            cmd = 'prop2po -t {0}/en.properties {0}/{2} ' \
                '--personality java --duplicates merge -o {1}'

            if self.conversor_setup is not None and \
               self.conversor_setup.type == 'string' and \
               self.conversor_setup.verb == 'add':
                cmd += self.conversor_setup.command
                logging.info('Adding parameter to conversor: {0}'.
                             format(self.conversor_setup.command))

            os.system(cmd.format(dirName, po_filename, prop_filename))

    def _convert_ini_files_to_po(self):

        for inifile in self.findFiles.find_recursive(self.convert_dir, '*.ini'):
            dirName = os.path.dirname(inifile)
            filename = os.path.basename(inifile)

            trg = None
            for filename in ['ca.ini', 'CA.ini', 'ca_ES.ini']:
                fullName = '{0}/{1}'.format(dirName, filename)
                if filename in inifile:
                    trg = fullName
                    break

            src = None
            for filename in ['en.ini', 'EN.ini', 'en_GB.ini']:
                fullName = '{0}/{1}'.format(dirName, filename)
                if os.path.isfile(fullName):
                    src = fullName
                    break

            if src is None or trg is None:
                continue

            # http://bugs.locamotion.org/show_bug.cgi?id=3148
            # The copy operations can be removed when the issue is fixed
            logging.info('convert ini file: {0}'.format(inifile))

            filename = '{0}/strings-ca.po'.format(dirName)
            convert_ini = ConvertIni(src, trg, filename).convert()

    def _convert_php_resources_files_to_po(self):
        if len(self.findFiles.find_recursive(self.convert_dir, '*.php')) == 0:
            return

        logging.info('convert php directory: {0}'.format(self.convert_dir))
        # Name arbitrary choosen (not sepecific to an expected dir structure)
        OUT_DIRNAME = 'po-files'
        cmd = 'cd {0} && php2po -t en -i ca ' \
              '-o {1}'.format(self.convert_dir, OUT_DIRNAME)
        os.system(cmd)

    '''
        Conditional conversion code for Android
        To be refactor when patterns for Android dir structure is clear
    '''
    def _process_non_standard_android_res_locations(self):

        '''Briar'''
        self._copy_res_files("translations/briar.stringsxml-5/en.xml",
                             "translations/briar.stringsxml-5/ca.xml")

        '''Telegram Android'''
        self._copy_res_files("translations/android/res/values/strings.xml",
                             "translations/android/res/values-ca/strings.xml")

        self._copy_res_files("translations/androidx/res/values/strings.xml",
                             "translations/androidx/res/values-ca/strings.xml")

        '''Runner Up'''
        self._copy_res_files("translations/runner-up-android.stringsxml/en.xml",
                             "translations/runner-up-android.stringsxml/ca.xml")



    def _copy_res_files(self, source_file, target_file):
        en_file = os.path.join(self.convert_dir, source_file)
        ca_file = os.path.join(self.convert_dir, target_file)

        if os.path.isfile(ca_file) == False or os.path.isfile(en_file) == False:
            return

        app_dir = 'android'
        directory = os.path.join(self.convert_dir, app_dir)
        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = os.path.join(self.convert_dir, app_dir, 'res')
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        directory = os.path.join(self.convert_dir, app_dir, 'res/values-ca')
        if not os.path.exists(directory):
            os.makedirs(directory)
                
        shutil.copy2(ca_file, os.path.join(directory, "strings.xml"))

        directory = os.path.join(self.convert_dir, app_dir, 'res/values')
        if not os.path.exists(directory):
            os.makedirs(directory)
                
        shutil.copy2(en_file, os.path.join(directory, "strings.xml"))
        self.android_dir = os.path.join(app_dir, 'res')

    def _process_briar_project(self):
        ca_file = os.path.join(self.convert_dir,
                               "translations/briar.stringsxml-5/ca.xml")

        en_file = os.path.join(self.convert_dir,
                               "translations/briar.stringsxml-5/en.xml")

        if os.path.isfile(ca_file) is False or os.path.isfile(en_file) is False:
            return

        directory = os.path.join(self.convert_dir, 'briar')
        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = os.path.join(self.convert_dir,'briar/res')
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        directory = os.path.join(self.convert_dir,'briar/res/values-ca')
        if not os.path.exists(directory):
            os.makedirs(directory)
                
        shutil.copy2(ca_file, os.path.join(directory, "strings.xml"))

        directory = os.path.join(self.convert_dir,'briar/res/values')
        if not os.path.exists(directory):
            os.makedirs(directory)
                
        shutil.copy2(en_file, os.path.join(directory, "strings.xml"))
        self.android_dir = 'briar/res'

    def _convert_android_resources_files_to_po(self):
        if len(self.findFiles.find_recursive(self.convert_dir, '*.xml')) == 0:
            return

        logging.info('convert Android directory: {0}'.format(self.convert_dir))
        # See: https://pypi.python.org/pypi/android2po/1.2.0
        # If you do not specify --gettext ., the file is writen in ../locale
        # outside the tmp directory in our case
        cmd = 'cd {0} && a2po init ca --gettext . > /dev/null'.format(self.convert_dir)

        self._process_non_standard_android_res_locations()

        if self.android_dir is not None:
            cmd += " --android {0}".format(self.android_dir)

        os.system(cmd)

    def _convert_json_file_to_po(self, jsonfile, source, target):
        dirName = os.path.dirname(jsonfile)
        logging.info('convert json file: {0}'.format(dirName))
        filename = '{0}/json-ca.po'.format(dirName)
        cmd = 'json2po -t {0}/{2} -i {0}/{3} ' \
              '-o {1}'.format(dirName, filename, source, target)
        os.system(cmd)
        print(cmd)

    def _convert_json_files_to_po(self):
        # Used for Privacy Badger
        for jsonfile in self.findFiles.find_recursive(self.convert_dir, 'messages.json'):
            if '/ca/' not in jsonfile:
                continue

            self._convert_json_file_to_po(jsonfile, '../en_US/messages.json', '../ca/messages.json')

        for jsonfile in self.findFiles.find_recursive(self.convert_dir, 'ca.json'):
            self._convert_json_file_to_po(jsonfile, 'en.json', 'ca.json')

    def _convert_yml_files_to_po(self):
        EXPECTED_SRC = 'en.yml'
        EXPECTED_TRG = 'ca.yml'

        for trgfile in self.findFiles.find_recursive(self.convert_dir, '*ca.yml'):
            srcfile = trgfile.replace("ca.yml", "en.yml")

            if os.path.isfile(srcfile) is False:
                continue

            dirName = os.path.dirname(srcfile)
            src_base = os.path.basename(srcfile)
            if src_base != EXPECTED_SRC:
                new = os.path.join(dirName, EXPECTED_SRC)
                shutil.copyfile(srcfile, new)

            trg_base = os.path.basename(trgfile)
            if trg_base != EXPECTED_TRG:
                new = os.path.join(dirName, EXPECTED_TRG)
                shutil.copyfile(trgfile, new)

            logging.info('convert yml file: {0}'.format(dirName))
            cmd = 'i18n-translate convert --locale_dir {0} -f yml -l ca -t po -d en'.format(dirName)
            os.system(cmd)

    def _convert_xliff_file_to_po(self):
        for xlfile in self.findFiles.find_recursive(self.convert_dir, '*.xliff'):
            fileName, fileExtension = os.path.splitext(xlfile)
            pofile = xlfile.replace(".xliff", ".po")
            cmd = f'xliff2po -i {xlfile} -o {pofile}'
            os.system(cmd)

