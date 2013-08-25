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
import urllib2
import os
import polib
import fnmatch
import time

class DownloadFile:

    def GetFile(self, url, filename):
        
        logging.info('Downloading file \'' + url + '\'' + " to " + filename)

        infile = urllib2.urlopen(url)
        output = open(filename,'wb')
        output.write(infile.read())
        output.close()

class POFile:

    def AddCommentToAllEntries(self, filename, comment):

        bakfile = filename + ".bak"

        os.system("cp " + filename + " " + bakfile)

        input_po = polib.pofile(bakfile)

        for entry in input_po:
            entry.tcomment = comment
            
        input_po.save(filename)

class FindFiles:

    def Find(self, directory, pattern):

        filelist = list()

        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    filelist.append(filename)

        filelist.sort()
        return filelist

class FileSet():

    temp_dir = "./tmp"

    def __init__(self, project, url, filename):
        self.project = project
        self.url = url
        self.filename = filename
        self.addSource = True
        self.excluded = list()

    def SetAddSource(self, addSource):
        self.addSource = addSource

    def SetTMFile(self, tmfile):
        self.tmfile = tmfile

    def AddExcluded(self, filename):
        self.excluded.append(filename)

    def AddComments(self):

        if (self.addSource == False):
            return

        findFiles = FindFiles()

        for filename in findFiles.Find(self.temp_dir, '*.po'):
            relative = filename.replace(self.temp_dir, '')
            pofile = POFile()
            pofile.AddCommentToAllEntries(filename, "Translation source: " + relative +  " from project '" + self.project + "'")

    def CleanUp(self):
        os.system("cp " + self.tmfile +" tm-project-previous.po")
        os.system("msgattrib tm-project-previous.po --no-fuzzy --no-obsolete --translated > " + self.tmfile)
        os.system("rm -f tm-project-previous.po")

    def ConvertTsFilesToPo(self):

        findFiles = FindFiles()

        for tsfile in findFiles.Find(self.temp_dir, '*.ts'):
            fileName, fileExtension = os.path.splitext(tsfile)
            logging.info("converting: " + fileName)
            os.system("ts2po " + tsfile + " -o " + fileName + ".po")

    def ConvertStringFilesToPo(self):

        findFiles = FindFiles()

        for tsfile in findFiles.Find(self.temp_dir, '*.strings'):
            dirName = os.path.dirname(tsfile);
            logging.info("convert: " + dirName)
            filename = dirName + "/strings-ca.po"
            os.system("prop2po -t " + dirName  + "/en.strings " + dirName + "/ca.strings --personality strings -o " + filename)
        
    def Build(self):

        findFiles = FindFiles()
        localtm = "tm-local.po"

        if (os.path.isfile(localtm)):
            os.system("rm -f " + localtm)

         # Build using a local memory translation file
        for filename in findFiles.Find(self.temp_dir, '*.po'):

            exclude = False
            for exfilename in self.excluded:
                if (filename.find(exfilename) != -1):
                    exclude = True

            if (exclude == True):
                logging.info( 'Excluding file:' + filename)
                continue

            logging.info('Adding file:' + filename + ' to translation memory')

            if (os.path.isfile(localtm)):
                os.system("cp " + localtm + " tm-project-previous.po")
                os.system("msgcat -tutf-8 --use-first -o " + localtm + " tm-project-previous.po " + filename)
                os.system("rm -f tm-project-previous.po")
            else:
                os.system("cp " + filename + " " + localtm)

        # Add to the project TM
        if (os.path.isfile(self.tmfile)):
            os.system("cp " + self.tmfile + " tm-project-previous.po")
            os.system("msgcat -tutf-8 --use-first -o " + self.tmfile + " tm-project-previous.po " + localtm)
            os.system("rm -f tm-project-previous.po")
        else:
            os.system("cp " + localtm + " " + self.tmfile)

        os.system("rm -f " + localtm)
        self.CleanUp()

    def Uncompress(self):

        os.system("rm -f -r " + self.temp_dir)

        if (self.filename.endswith('zip')):
            os.system("unzip " + self.filename + " -d " + self.temp_dir)
        elif (self.filename.endswith('tar.gz')):
            os.system("mkdir " + self.temp_dir)
            os.system("tar -xvf " + self.filename + " -C " + self.temp_dir)
        elif (self.filename.endswith('.po') or  self.filename.endswith('.ts')):
            os.system("mkdir " + self.temp_dir)
            os.system("cp " + self.filename + " " + self.temp_dir + "/" + self.filename)
        else:
            logging.error("Unsupported file extension for filename " + self.filename)




