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


import os
import logging

from localfileset import LocalFileSet
from compressedfileset import CompressedFileSet
from bazaarfileset import BazaarFileSet
from transifexfileset import TransifexFileSet
from localdirfileset import LocalDirFileSet
from filefileset import FileFileSet
from polib import pofile


class Project:

    def __init__(self, name, filename):
        self.addSource = True
        self.filename = filename
        self.filesets = list()
        self.name = name

    def GetFilename(self):
        return self.filename

    def SetAddSource(self, addSource):
        self.addSource = addSource

    def DeletePOFile(self):
        if (os.path.isfile(self.filename)):
            os.system("rm " + self.filename)

    def Add(self, fileset):
        fileset.SetTMFile(self.filename)
        self.filesets.append(fileset)

    def AddFileSets(self, project_dto):

        for fileset in project_dto.filesets:
            logging.debug(fileset)

            if (fileset.type == 'local-file'):
                fs = LocalFileSet(fileset.name, fileset.url, fileset.target)
            elif (fileset.type == 'compressed'):
                fs = CompressedFileSet(fileset.name, fileset.url,
                                       fileset.target)
            elif (fileset.type == 'bazaar'):
                fs = BazaarFileSet(fileset.name, fileset.url, fileset.target)
            elif (fileset.type == 'transifex'):
                fs = TransifexFileSet(fileset.name, fileset.url,
                                      fileset.target)
            elif (fileset.type == 'local-dir'):
                fs = LocalDirFileSet(fileset.name, fileset.url, fileset.target)
            elif (fileset.type == 'file'):
                fs = FileFileSet(fileset.name, fileset.url, fileset.target)

            self.Add(fs)
            fs.AddExcluded(fileset.excluded)

    def Do(self):
        try:
            self.DeletePOFile()

            for fileset in self.filesets:
                fileset.SetAddSource(self.addSource)
                fileset.Do()

        except Exception as detail:
            logging.error("Project.Do. Cannot complete " + self.filename)
            logging.error(detail)
            self.DeletePOFile()

    def Statistics(self):

        poFile = pofile(self.filename)

        words = 0
        for entry in poFile:
            string_words = entry.msgstr.split(' ')
            words += len(string_words)

        s = self.name + " project. " + str(len(poFile.translated_entries()))
        s = s + " translated strings, words " + str(words)

        logging.info(s)

    def ToTmx(self):

        fileName, fileExtension = os.path.splitext(self.filename)
        os.system("po2tmx " + self.filename + " --comment others -l ca-ES -o "
                  + fileName + ".tmx")
