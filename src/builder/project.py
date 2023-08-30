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
from .zanatafileset import ZanataFileSet
from .pontoonfileset import PontoonFileSet
from .mercurialfileset import MercurialFileSet
from .weblatefileset import WeblateFileSet
from .crowdinfileset import CrowdinFileSet
import re


class Project(object):
    def __init__(self, name, project_id, filename):
        self.add_source = True
        self.filename = filename
        self.filesets = []
        self.name = name
        self.project_id = project_id
        self.checksum = None
        self.report_errors = True
        self.out_directory = ""
        self.license = ""

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

            if fileset.type == "local-file":
                fs = LocalFileSet(
                    self.name,
                    self.project_id,
                    fileset.name,
                    fileset.url,
                    fileset.target,
                )
            elif fileset.type == "compressed":
                fs = CompressedFileSet(
                    self.name,
                    self.project_id,
                    fileset.name,
                    fileset.url,
                    fileset.target,
                )
            elif fileset.type == "bazaar":
                fs = BazaarFileSet(
                    self.name,
                    self.project_id,
                    fileset.name,
                    fileset.url,
                    fileset.target,
                )
            elif fileset.type == "transifex":
                fs = TransifexFileSet(
                    self.name,
                    self.project_id,
                    fileset.name,
                    fileset.url,
                    fileset.target,
                )
            elif fileset.type == "transifexhub":
                fs = TransifexHubFileSet(
                    self.name,
                    self.project_id,
                    fileset.name,
                    fileset.url,
                    fileset.target,
                )
                fs.set_project(self)
            elif fileset.type == "local-dir":
                fs = LocalDirFileSet(
                    self.name,
                    self.project_id,
                    fileset.name,
                    fileset.url,
                    fileset.target,
                )
            elif fileset.type == "file":
                fs = FileFileSet(
                    self.name,
                    self.project_id,
                    fileset.name,
                    fileset.url,
                    fileset.target,
                )
            elif fileset.type == "subversion":
                fs = SubversionFileSet(
                    self.name,
                    self.project_id,
                    fileset.name,
                    fileset.url,
                    fileset.target,
                )
            elif fileset.type == "crawl":
                fs = CrawlFileSet(
                    self.name,
                    self.project_id,
                    fileset.name,
                    fileset.url,
                    fileset.target,
                )
                fs.set_retrieval_pattern(fileset.retrieval_pattern)
            elif fileset.type == "git":
                fs = GitFileSet(
                    self.name,
                    self.project_id,
                    fileset.name,
                    fileset.url,
                    fileset.target,
                )
            elif fileset.type == "gerrit-directory":
                fs = GerritDirectoryFileSet(
                    self.name,
                    self.project_id,
                    fileset.name,
                    fileset.url,
                    fileset.target,
                )
                fs.set_project(self)
                fs.set_retrieval_pattern(fileset.retrieval_pattern)
            elif fileset.type == "zanata":
                fs = ZanataFileSet(
                    self.name,
                    self.project_id,
                    fileset.name,
                    fileset.url,
                    fileset.target,
                )
            elif fileset.type == "pontoon":
                fs = PontoonFileSet(
                    self.name,
                    self.project_id,
                    fileset.name,
                    fileset.url,
                    fileset.target,
                )
                fs.set_project(self)
            elif fileset.type == "mercurial":
                fs = MercurialFileSet(
                    self.name,
                    self.project_id,
                    fileset.name,
                    fileset.url,
                    fileset.target,
                )
            elif fileset.type == "weblate":
                fs = WeblateFileSet(
                    self.name,
                    self.project_id,
                    fileset.name,
                    fileset.url,
                    fileset.target,
                )
                fs.set_retrieval_pattern(fileset.retrieval_pattern)
            elif fileset.type == "crowdin":
                fs = CrowdinFileSet(
                    self.name,
                    self.project_id,
                    fileset.name,
                    fileset.url,
                    fileset.target,
                )
            else:
                msg = "Unsupported filetype: {0}".format(fileset.type)
                logging.error(msg)
                raise Exception(msg)

            fs.set_pattern(fileset.pattern)
            fs.set_duplicates(fileset.duplicates)
            fs.set_conversor_setup(fileset.conversor_setup)
            fs.set_po_preprocessing(fileset.po_preprocessing)
            self.add_fileset(fs)

    def do(self):
        start_time = datetime.datetime.now()
        self._delete_po_file()
        checksum = hashlib.new("sha1")

        for fileset in self.filesets:
            fileset.expand_dynamic()

        for fileset in self.filesets:
            try:
                fileset.set_checksum(checksum)
                fileset.set_add_source(self.add_source)
                fileset.do_withtemp()

                if self.report_errors is True and fileset.words < 0:
                    logging.error(
                        "Project {0}, fileset {1}, words {2}".format(
                            self.name, fileset.name, fileset.words
                        )
                    )

            except Exception as detail:
                msg = "Project.do. Cannot complete project {0}, fileset {1}".format(
                    self.name, fileset.name
                )
                logging.exception(msg.format(self.filename))
                logging.error(detail)

        self.checksum = checksum.hexdigest()

        logging.info(
            "Time used to build project {0}: {1}".format(
                self.name, datetime.datetime.now() - start_time
            )
        )
        return self.checksum

    def get_words_entries(self):
        words = 0
        entries = 0

        try:
            filename = self._get_filename_at_output(self.filename)
            poFile = pofile(filename)

            for entry in poFile:
                string_words = entry.msgstr.split(" ")
                words += len(string_words)

            entries = len(poFile.translated_entries())

        except Exception:
            msg = "Project.get_words_entries exception {0}"
            logging.error(msg.format(filename))
            words = entries = -1

        return words, entries

    def statistics(self):
        words, entries = self.get_words_entries()
        if words == 0:
            logging.error(f"{self.name} project has {words} words")

        logging.info(
            f"{self.name} project. {entries} translated strings, words {words}"
        )

    def _get_filename_at_output(self, filename):
        return os.path.join(self.out_directory, filename)

    def to_tmx(self):
        fullpath_filename = self._get_filename_at_output(self.filename)
        if os.path.isfile(fullpath_filename) is False:
            return

        fileName, fileExtension = os.path.splitext(self.filename)
        cmd = 'po2tmx "{0}" -l ca -o "{1}.tmx"'
        cmd = cmd.format(fullpath_filename, self._get_filename_at_output(fileName))
        os.system(cmd)
