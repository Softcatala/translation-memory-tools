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

import hashlib
import logging
import os
import datetime
from polib import pofile

from .bazaarfileset import BazaarFileSet
from .compressedfileset import CompressedFileSet
from .crawlerfileset import CrawlFileSet
from .filefileset import FileFileSet
from .gerritdirectoryfileset import GerritDirectoryFileSet
from .gitfileset import GitFileSet
from .localdirfileset import LocalDirFileSet
from .localfileset import LocalFileSet
from .subversionfileset import SubversionFileSet
from .transifexfileset import TransifexFileSet
from .transifexhubfileset import TransifexHubFileSet
from .gitwebfileset import GitWebFileSet
from .transvisionfileset import TransvisionFileSet
from .xiaomifileset import XiaomiFileSet
from .cgitfileset import CGitFileSet

class Project(object):

    def __init__(self, name, filename):
        self.add_source = True
        self.filename = filename
        self.filesets = []
        self.name = name
        self.checksum = None
        self.report_errors = True
        self.out_directory = ""

    def get_filename(self):
        return self.filename

    def get_filename_fullpath(self):
        return self._get_filename_at_output(self.filename)

    def set_add_source(self, add_source):
        self.add_source = add_source

    def set_out_directory(self, out_directory):
        self.out_directory = out_directory

    def _delete_po_file(self):
        filename = self._get_filename_at_output(self.filename)
        if os.path.isfile(filename):
            os.remove(filename)

    def add_fileset(self, fileset):
        fileset.set_tm_file(self.filename)
        fileset.set_out_directory(self.out_directory)
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
            elif fileset.type == 'transifexhub':
                fs = TransifexHubFileSet(self.name,
                                      fileset.name,
                                      fileset.url,
                                      fileset.target)
                fs.set_project(self)
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
            elif fileset.type == 'gitweb':
                fs = GitWebFileSet(self.name,
                                  fileset.name,
                                  fileset.url,
                                  fileset.target)
                fs.set_pattern(fileset.pattern)
                fs.set_project(self)
            elif fileset.type == 'transvision':
                fs = TransvisionFileSet(self.name,
                                  fileset.name,
                                  fileset.url,
                                  fileset.target)
            elif fileset.type == 'xiaomi':
                fs = XiaomiFileSet(self.name,
                                  fileset.name,
                                  fileset.url,
                                  fileset.target)
            elif fileset.type == 'cgit':
                fs = CGitFileSet(self.name,
                                  fileset.name,
                                  fileset.url,
                                  fileset.target)
                fs.set_pattern(fileset.pattern)
                fs.set_project(self)
            else:
                msg = 'Unsupported filetype: {0}'
                logging.error(msg.format(fileset.type))

            fs.add_excluded(fileset.excluded)
            fs.set_duplicates(fileset.duplicates)
            fs.set_conversor_setup(fileset.conversor_setup)
            fs.set_remove_untranslated(fileset.remove_untranslated)
            self.add_fileset(fs)

    def do(self):
        start_time = datetime.datetime.now()
        self._delete_po_file()
        checksum = hashlib.new('sha1')

        for fileset in self.filesets:
            try:

                fileset.set_checksum(checksum)
                fileset.set_add_source(self.add_source)
                fileset.do_withtemp()

                if self.report_errors is True and fileset.words <= 0:
                    logging.error('Project {0}, fileset {1}, words {2}'.format(
                                self.name, fileset.name, fileset.words))

            except Exception as detail:
                msg = 'Project.do. Cannot complete project {0}, fileset {1}'. \
                      format(self.name, fileset.name)
                logging.exception(msg.format(self.filename))
                logging.error(detail)
                pass

        self.checksum = checksum.hexdigest()

        logging.info('Time need to build project {0}: {1}'.format(self.name,
                     datetime.datetime.now() - start_time))

    def get_words_entries(self):

        words = -1
        entries = -1

        try:
            filename = self._get_filename_at_output(self.filename)
            poFile = pofile(filename)

            for entry in poFile:
                string_words = entry.msgstr.split(' ')
                words += len(string_words)

            entries = len(poFile.translated_entries())

        except Exception as detail:
            msg = 'Project.get_words_entries exception {0}'
            logging.error(msg.format(filename))

        return words, entries

    def statistics(self):
        words, entries = self.get_words_entries()
        msg = '{0} project. {1} translated strings, words {2}'
        logging.info(msg.format(self.name, entries, words))

    def _get_filename_at_output(self, filename):
        return os.path.join(self.out_directory, filename)

    def to_tmx(self):
        fileName, fileExtension = os.path.splitext(self.filename)
        # TODO: Once a translate toolkit version > 1.10 has been published
        # (https://github.com/translate/translate/releases) we can deploy
        # the version and add the comment parameter to allow export comments
        # to TMX
        # cmd = 'po2tmx {0} --comment others -l ca-ES -o {1}.tmx'
        cmd = 'po2tmx "{0}" -l ca-ES -o "{1}.tmx"'
        cmd = cmd.format(self._get_filename_at_output(self.filename), 
                         self._get_filename_at_output(fileName))
        os.system(cmd)
