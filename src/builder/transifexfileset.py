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

from .fileset import FileSet
from .findfiles import FindFiles


class TransifexFileSet(FileSet):
    def clean_up_after_convert(self):
        self._remove_english_files()
        self._remove_non_translation_files()

    # Transifex keeps source files and we need to filter them out
    def _remove_english_files(self):
        findFiles = FindFiles()

        for filename in findFiles.find_recursive(self.temp_dir, "*"):
            if (
                filename.endswith("en.po")
                or filename.endswith("en.ts")
                or filename.endswith("en_GB.po")
                or filename.endswith("en_GB.ts")
                or filename.endswith("en_US.po")
                or filename.endswith("en_US.ts")
            ):
                os.remove(filename)

    def do(self):
        prevdir = os.getcwd()
        os.chdir(self.temp_dir)

        os.system("tx init")
        os.system(
            "tx add remote --file-filter 'translations/<project_slug>.<resource_slug>/<lang>.<ext>' {0}".format(
                self.url
            )
        )

        # To be able to process files with no English source (.strings, .xml,
        # etc) we pull the English files too and then we delete the ones that
        # include source and target
        cmd = "tx pull -f -s -t -l ca,ca_ES,en,en_GB"
        os.system(cmd)
        os.chdir(prevdir)
        self.build()
