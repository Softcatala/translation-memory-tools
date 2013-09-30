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


import os
import logging

from localfileset import LocalFileSet
from compressedfileset import CompressedFileSet
from bazaarfileset import BazaarFileSet
from transifexfileset import TransifexFileSet
from localdirfileset import LocalDirFileSet
from filefileset import FileFileSet
from subversionfileset import SubversionFileSet
from polib import pofile
from crawlerfileset import CrawlFileSet

class Project:

    def __init__(self, name, filename):
        self.add_source = True
        self.filename = filename
        self.filesets = list()
        self.name = name

    def get_filename(self):
        return self.filename

    def set_add_source(self, add_source):
        self.add_source = add_source

    def _delete_po_file(self):
        if (os.path.isfile(self.filename)):
            os.system("rm " + self.filename)

    def add(self, fileset):
        fileset.set_tm_file(self.filename)
        self.filesets.append(fileset)

    def add_filesets(self, project_dto):

        for fileset in project_dto.filesets:
            logging.debug(fileset)

            if (fileset.type == 'local-file'):
                fs = LocalFileSet(fileset.name, fileset.url, fileset.target)
            elif (fileset.type == 'compressed'):
                fs = CompressedFileSet(fileset.name, fileset.url,
                                       fileset.target)
                fs.set_pattern(fileset.pattern)
            elif (fileset.type == 'bazaar'):
                fs = BazaarFileSet(fileset.name, fileset.url, fileset.target)
                fs.set_pattern(fileset.pattern)
            elif (fileset.type == 'transifex'):
                fs = TransifexFileSet(fileset.name, fileset.url,
                                      fileset.target)
            elif (fileset.type == 'local-dir'):
                fs = LocalDirFileSet(fileset.name, fileset.url, fileset.target)
            elif (fileset.type == 'file'):
                fs = FileFileSet(fileset.name, fileset.url, fileset.target)
            elif (fileset.type == 'subversion'):
                fs = SubversionFileSet(fileset.name, fileset.url, fileset.target)
            elif (fileset.type == 'crawl'):
                fs = CrawlFileSet(fileset.name, fileset.url, fileset.target)
                fs.set_pattern(fileset.pattern)
            else:
                logging.error("Unsupported filetype: " + fileset.type)

            self.add(fs)
            fs.add_excluded(fileset.excluded)

    def do(self):
        try:
            self._delete_po_file()

            for fileset in self.filesets:
                fileset.set_add_source(self.add_source)
                fileset.do()

        except Exception as detail:
            logging.error("Project.do. Cannot complete " + self.filename)
            logging.error(detail)
            self._delete_po_file()

    def statistics(self):

        words = 0
        entries = 0

        try:

            poFile = pofile(self.filename)

            for entry in poFile:
                string_words = entry.msgstr.split(' ')
                words += len(string_words)

            entries = str(len(poFile.translated_entries()))

        except Exception as detail:
            logging.error("Project. statistics exception " + self.filename)
            logging.error(detail)


        finally:
            s = self.name + " project. " + str(entries)
            s = s + " translated strings, words " + str(words)
            logging.info(s)

    def to_tmx(self):

        fileName, fileExtension = os.path.splitext(self.filename)
        os.system("po2tmx " + self.filename + " --comment others -l ca-ES -o "
                  + fileName + ".tmx")
