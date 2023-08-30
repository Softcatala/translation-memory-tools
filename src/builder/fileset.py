# -*- coding: utf-8 -*-
#
# Copyright (c) 2012-2014 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import re

from .convertfiles import ConvertFiles
from .findfiles import FindFiles
from .pocatalog import POCatalog
from .pofile import POFile
import tempfile


class FileSet:
    invidual_pos_dir = ""

    def __init__(
        self, project_name, project_id, name, url, filename, parent_fileset=None
    ):
        self.project_name = project_name
        self.name = name
        self.project_id = project_id
        self.url = url
        self.filename = filename
        self.add_source = True
        self.po_catalog = None
        self.words = -1
        self.duplicates = ""
        self.set_out_directory("")
        self.retrieval_pattern = ""
        self.pattern = ""

        satanized = re.sub(r"[^\.a-zA-Z0-9_-]+", "", self.filename)
        # print(f"*********** FILESET. org: {self.filename}, satanized: {satanized}")
        self.filename = satanized

        prefix = re.sub(r"[^\.a-zA-Z0-9_-]+", "", project_name)
        prefix = prefix[0 : min(6, len(prefix))]
        self.temp_dir = tempfile.TemporaryDirectory(prefix=f"{prefix}_").name

        if parent_fileset:
            self.conversor_setup = parent_fileset.conversor_setup
            self.po_preprocessing = parent_fileset.po_preprocessing
        else:
            self.conversor_setup = None
            self.po_preprocessing = ""

    def set_checksum(self, checksum):
        self.checksum = checksum

    def set_retrieval_pattern(self, retrieval_pattern):
        self.retrieval_pattern = retrieval_pattern

    def set_out_directory(self, out_directory):
        POS_DIR = "individual_pos/"
        self.out_directory = out_directory
        self.invidual_pos_dir = os.path.join(
            out_directory, POS_DIR, self.project_id, self.name.lower()
        )

    def set_add_source(self, add_source):
        self.add_source = add_source

    def set_duplicates(self, duplicates):
        self.duplicates = duplicates

    def set_conversor_setup(self, conversor):
        self.conversor_setup = conversor

    def set_pattern(self, pattern):
        self.pattern = pattern

    def set_tm_file(self, tm_file):
        self.tm_file = tm_file

    def set_po_preprocessing(self, po_preprocessing):
        self.po_preprocessing = po_preprocessing

    def add_comments(self):
        if not self.add_source:
            return

        findFiles = FindFiles()
        for filename in findFiles.find_recursive(self.temp_dir, "*.po"):
            relative = filename.replace(self.temp_dir, "")
            pofile = POFile(filename)

            if self.project_name.lower().strip() == self.name.lower().strip():
                msg = "Source: {0} from project '{1}'".format(
                    relative, self.project_name
                )
            else:
                msg = "Source: {0} from project '{1} - {2}'".format(
                    relative, self.project_name, self.name
                )

            self.words += pofile.get_statistics()

            pofile.add_comment_to_all_entries_and_remove_fuzzys(msg)
            pofile.calculate_localized_string_checksum(self.checksum)

    def _po_preprocessing(self):
        if len(self.po_preprocessing) == 0:
            return

        findFiles = FindFiles()
        for filename in findFiles.find_recursive(self.temp_dir, "*.po"):
            pofile = POFile(filename)
            pofile.po_preprocessing(self.po_preprocessing)

    def clean_up_after_convert(self):
        self._remove_non_translation_files()

    def _build_tm_for_fileset(self, fileset_tm, files):
        for filename in files:
            pofile = POFile(filename)
            if self.duplicates == "msgctxt":
                pofile.add_msgctxt_to_duplicates()

            words = pofile.get_statistics()
            msg = f"Adding file: {filename} to translation memory with {words} words"
            logging.info(msg)
            self.po_catalog.add_pofile(filename)

    def _add_tm_for_fileset_to_project_tm(self, fileset_tm):
        filename = os.path.join(self.out_directory, self.tm_file)
        project_catalog = POCatalog(filename)
        project_catalog.add_pofile(self.po_catalog.filename)
        project_catalog.cleanup()

    def do_withtemp(self):
        self._create_tmp_directory()
        self.do()
        self._remove_tmp_directory()

    def expand_dynamic(self):
        pass

    def build(self):
        convert = ConvertFiles(self.temp_dir, self.conversor_setup)
        convert.convert()

        self.clean_up_after_convert()
        self._po_preprocessing()
        self.add_comments()

        findFiles = FindFiles()
        files = findFiles.find_recursive(self.temp_dir, "*.po")

        if len(files) == 0:
            logging.info("No files to add in fileset: {0}".format(self.name))
            return

        prefix = self.name[0 : min(6, len(self.name))]
        with tempfile.NamedTemporaryFile(prefix=f"{prefix}_") as tmp:
            fileset_tm = tmp.name
            self.po_catalog = POCatalog(fileset_tm)
            self._build_tm_for_fileset(fileset_tm, files)
            self._add_tm_for_fileset_to_project_tm(fileset_tm)
            self._copy_to_output()

    def _copy_to_output(self):
        if not os.path.exists(self.invidual_pos_dir):
            os.makedirs(self.invidual_pos_dir)

        findFiles = FindFiles()
        files = findFiles.find_recursive(self.temp_dir, "*.po")
        for source in files:
            dirname = os.path.dirname(source)
            if dirname != self.temp_dir:
                d = os.path.join(
                    self.invidual_pos_dir, dirname[len(self.temp_dir) + 1 :]
                )
                if not os.path.exists(d):
                    os.makedirs(d)

            target = os.path.join(
                self.invidual_pos_dir, source[len(self.temp_dir) + 1 :]
            )
            shutil.copy(source, target)

    def _create_tmp_directory(self):
        self._remove_tmp_directory()
        os.makedirs(self.temp_dir)

    def _remove_tmp_directory(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def is_retrieval_pattern(self, item):
        return re.match(self.retrieval_pattern, item)

    def _remove_non_translation_files(self):
        """
        We clean up other PO files like fr.po, es.po, to prevent to be
        added to the translation memory
        """

        if self.pattern is None or len(self.pattern) == 0:
            return

        findFiles = FindFiles()

        for filename in findFiles.find_recursive(self.temp_dir, "*"):
            if re.match(self.pattern, filename) is None and os.path.exists(filename):
                os.remove(filename)
