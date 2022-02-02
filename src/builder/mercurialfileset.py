# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import re
import shutil

from .fileset import FileSet
from .findfiles import FindFiles


class MercurialFileSet(FileSet):

    hg_dir = '_hg'

    def set_pattern(self, pattern):
        self.pattern = pattern

    def _get_filename(self):
        filename = self.url.split('/')[-1]
        return filename

    def _remove_non_translation_files(self):
        '''
            We clean up other PO files like fr.po, es.po, to prevent to be
            added to the translation memory
        '''

        if self.pattern is None or len(self.pattern) == 0:
            return

        findFiles = FindFiles()

        for filename in findFiles.find_recursive(self.temp_dir, '*'):

            if re.match(self.pattern, filename) is None and \
                    os.path.exists(filename):
                os.remove(filename)

    def clean_up_after_convert(self):
        self._remove_non_translation_files()

    def _remove_hg_directory(self):
        if os.path.exists(self.hg_dir):
            shutil.rmtree(self.hg_dir)

    def download(self):
        self._remove_hg_directory()
        cmd = 'cd {0} && hg clone {1} {2}'.format(
            self.temp_dir, self.url, self.hg_dir)
        os.system(cmd)

        # Move it to the root to avoid git default behavior to clone
        # into a subdirectory
        cmd = 'cd {0} && mv {1}/* . && rm -r -f {1}'.format(self.temp_dir, self.hg_dir)
        os.system(cmd)

    def do(self):
        self.download()
        self.build()
