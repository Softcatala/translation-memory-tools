# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from fileset import FileSet
from findfiles import FindFiles


class GitFileSet(FileSet):

    def set_pattern(self, pattern):
        self.pattern = pattern

    def _get_filename(self):
        filename = self.url.split('/')[-1]
        return filename

    def _remove_non_translation_files(self):
        findFiles = FindFiles()

        for filename in findFiles.find(self.temp_dir, '*'):

            if re.match(self.pattern, filename) is None and \
                    os.path.exists(filename):
                os.remove(filename)

    def do(self):
        self.create_tmp_directory()

        cmd = 'cd {0} && git clone --depth=1 {1} _git'.format(
            self.temp_dir, self.url)
        os.system(cmd)

        # Move it to the root to avoid git default behavior to clone
        # into a subdirectory
        cmd = 'cd {0} && mv _git/* .'.format(self.temp_dir)
        os.system(cmd)

        self._remove_non_translation_files()
        self.build()
        self.remove_tmp_directory()
