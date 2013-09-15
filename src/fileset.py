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

from pofile import POFile
from findfiles import FindFiles


class FileSet():

    temp_dir = "./tmp"

    def __init__(self, project, url, filename):
        self.project = project
        self.url = url
        self.filename = filename
        self.add_source = True
        self.excluded = list()

    def set_add_source(self, add_source):
        self.add_source = add_source

    def set_tm_file(self, tm_file):
        self.tm_file = tm_file

    def add_excluded(self, filename):

        if len(filename) > 0:
            self.excluded.append(filename)

    def add_comments(self):

        if (self.add_source is False):
            return

        findFiles = FindFiles()

        for filename in findFiles.find(self.temp_dir, '*.po'):
            relative = filename.replace(self.temp_dir, '')
            pofile = POFile()
            pofile.add_comment_to_all_entries(filename, "Translation source: " + relative + " from project '" + self.project + "'")

    def _clean_up(self):
        os.system("cp " + self.tm_file + " tm-project-previous.po")
        os.system("msgattrib tm-project-previous.po --no-fuzzy --no-obsolete --translated > " + self.tm_file)
        os.system("rm -f tm-project-previous.po")

    def convert_ts_files_to_po(self):

        findFiles = FindFiles()

        for tsfile in findFiles.find(self.temp_dir, '*.ts'):
            fileName, fileExtension = os.path.splitext(tsfile)
            logging.info("converting: " + fileName)
            os.system("ts2po " + tsfile + " -o " + fileName + ".po")

    def convert_string_files_to_po(self):

        findFiles = FindFiles()

        for tsfile in findFiles.find(self.temp_dir, '*.strings'):
            dirName = os.path.dirname(tsfile)
            logging.info("convert: " + dirName)
            filename = dirName + "/strings-ca.po"
            os.system("prop2po -t " + dirName + "/en.strings " + dirName + "/ca.strings --personality strings -o " + filename)
            
    def convert_ini_files_to_po(self):

        findFiles = FindFiles()

        for tsfile in findFiles.find(self.temp_dir, '*.ini'):
            dirName = os.path.dirname(tsfile)
            logging.info("convert: " + dirName)
            filename = dirName + "/strings-ca.po"
            os.system("prop2po -t " + dirName + "/en.ini " + dirName + "/ca.ini --encoding=utf-8 --personality=strings -o " + filename)

    def build(self):

        findFiles = FindFiles()
        localtm = "tm-local.po"

        if (os.path.isfile(localtm)):
            os.system("rm -f " + localtm)

        # Build using a local memory translation file
        for filename in findFiles.find(self.temp_dir, '*.po'):

            exclude = False
            for exfilename in self.excluded:
                if (filename.find(exfilename) != -1):
                    exclude = True

            if (exclude is True):
                logging.info('Excluding file:' + filename)
                continue

            logging.info('Adding file:' + filename + ' to translation memory')

            if (os.path.isfile(localtm)):
                os.system("cp " + localtm + " tm-project-previous.po")
                os.system("msgcat -tutf-8 --use-first -o " + localtm + " tm-project-previous.po " + filename)
                os.system("rm -f tm-project-previous.po")
            else:
                os.system("cp " + filename + " " + localtm)

        # Add to the project TM
        if (os.path.isfile(self.tm_file)):
            os.system("cp " + self.tm_file + " tm-project-previous.po")
            os.system("msgcat -tutf-8 --use-first -o " + self.tm_file + " tm-project-previous.po " + localtm)
            os.system("rm -f tm-project-previous.po")
        else:
            os.system("cp " + localtm + " " + self.tm_file)

        os.system("rm -f " + localtm)
        self._clean_up()
        
    def create_tmp_directory(self):
        os.system("rm -f -r " + self.temp_dir)
        os.system("mkdir " + self.temp_dir)
        
    def remove_tmp_directory(self):
        os.system("rm -f -r " + self.temp_dir)

    def uncompress(self):

        if (self.filename.endswith('.zip')):
            os.system("unzip " + self.filename + " -d " + self.temp_dir)
        elif (self.filename.endswith('tar.gz')):
            os.system("mkdir " + self.temp_dir)
            os.system("tar -xvf " + self.filename + " -C " + self.temp_dir)
        elif (self.filename.endswith('.gz')):
            os.system("mkdir " + self.temp_dir)
            # We are assuming that the .gz file will contain a single PO
            os.system("gunzip " + self.filename + " -c > " + self.temp_dir
                      + "/ca.po")
        elif (self.filename.endswith('.po') or self.filename.endswith('.ts')):
            os.system("mkdir " + self.temp_dir)
            os.system("cp " + self.filename + " " + self.temp_dir + "/" + self.filename)
        elif (self.filename.endswith('tar.xz')):
            os.system("mkdir " + self.temp_dir)
            os.system("tar -Jxf " + self.filename + " -C " + self.temp_dir)
        else:
            logging.error("Unsupported file extension for filename:" + self.filename)
