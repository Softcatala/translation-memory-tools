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

from bazaarfileset import BazaarFileSet
from compressedfileset import CompressedFileSet
from crawlerfileset import CrawlFileSet
from filefileset import FileFileSet
from localdirfileset import LocalDirFileSet
from localfileset import LocalFileSet
from polib import pofile
from subversionfileset import SubversionFileSet
from transifexfileset import TransifexFileSet
from gitfileset import GitFileSet
from gerritdirectoryfileset import GerritDirectoryFileSet

import logging
import os


class Project:

    def __init__(self, name, filename):
        self.add_source = True
        self.filename = filename
        self.filesets = []
        self.name = name

    def get_filename(self):
        return self.filename

    def set_add_source(self, add_source):
        self.add_source = add_source

    def _delete_po_file(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def add(self, fileset):
        fileset.set_tm_file(self.filename)
        self.filesets.append(fileset)

    def add_filesets(self, project_dto):
        for fileset in project_dto.filesets:
            logging.debug(fileset)

            if fileset.type == 'local-file':
                fs = LocalFileSet(self.name,
                                  fileset.name,
                                  fileset.url,
                                  fileset.target)
            elif fileset.type == 'compressed':
                fs = CompressedFileSet(self.name,
                                       fileset.name,
                                       fileset.url,
                                       fileset.target)
                fs.set_pattern(fileset.pattern)
            elif fileset.type == 'bazaar':
                fs = BazaarFileSet(self.name,
                                   fileset.name,
                                   fileset.url,
                                   fileset.target)
                fs.set_pattern(fileset.pattern)
            elif fileset.type == 'transifex':
                fs = TransifexFileSet(self.name,
                                      fileset.name,
                                      fileset.url,
                                      fileset.target)
            elif fileset.type == 'local-dir':
                fs = LocalDirFileSet(self.name,
                                     fileset.name,
                                     fileset.url,
                                     fileset.target)
            elif fileset.type == 'file':
                fs = FileFileSet(self.name,
                                 fileset.name,
                                 fileset.url,
                                 fileset.target)
            elif fileset.type == 'subversion':
                fs = SubversionFileSet(self.name,
                                       fileset.name,
                                       fileset.url,
                                       fileset.target)
            elif fileset.type == 'crawl':
                fs = CrawlFileSet(self.name,
                                  fileset.name,
                                  fileset.url,
                                  fileset.target)
                fs.set_pattern(fileset.pattern)
            elif fileset.type == 'git':
                fs = GitFileSet(self.name,
                                  fileset.name,
                                  fileset.url,
                                  fileset.target)
                fs.set_pattern(fileset.pattern)
            elif fileset.type == 'gerrit-directory':
                fs = GerritDirectoryFileSet(self.name,
                                  fileset.name,
                                  fileset.url,
                                  fileset.target)
                fs.set_pattern(fileset.pattern)
                fs.set_project(self)
            else:
                msg = 'Unsupported filetype: {0}'
                logging.error(msg.format(fileset.type))

            self.add(fs)
            fs.add_excluded(fileset.excluded)

    def do(self):
        self._delete_po_file()

        for fileset in self.filesets:
            try:

                fileset.set_add_source(self.add_source)
                fileset.do()

            except Exception as detail:
                msg = 'Project.do. Cannot complete project {0}, fileset {1}'. \
                      format(self.name, fileset.name)
                logging.exception(msg.format(self.filename))
                logging.error(detail)
                pass

    def statistics(self):
        words = 0
        entries = 0

        try:
            poFile = pofile(self.filename)

            for entry in poFile:
                string_words = entry.msgstr.split(' ')
                words += len(string_words)

            entries = len(poFile.translated_entries())

        except Exception as detail:
            msg = 'Project. statistics exception {0}'
            logging.error(msg.format(self.filename))
            logging.error(detail)

        finally:
            msg = '{0} project. {1} translated strings, words {2}'
            logging.info(msg.format(self.name, entries, words))

    def to_tmx(self):
        fileName, fileExtension = os.path.splitext(self.filename)
        # TODO: Once a translate toolkit version > 1.10 has been published
        # (https://github.com/translate/translate/releases) we can deploy
        # the version and add the comment parameter to allow export comments
        # to TMX
        #cmd = 'po2tmx {0} --comment others -l ca-ES -o {1}.tmx'
        cmd = 'po2tmx {0} -l ca-ES -o {1}.tmx'
        os.system(cmd.format(self.filename, fileName))
