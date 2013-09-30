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
import re

from fileset import FileSet
from findfiles import FindFiles


class BazaarFileSet(FileSet):

    def set_pattern(self, pattern):
        self.pattern = pattern

    def _has_filename(self):
        '''Used to identify if the file contains a path (/ and then .)'''
        filename = self.url.split('/')[-1]

        if len(filename) > 0:
            rslt = self.filename.find('.')
            if rslt != -1:
                return True

        return False

    def _remove_non_translation_files(self):
        findFiles = FindFiles()

        for filename in findFiles.find(self.temp_dir, '*'):

            if re.match(self.pattern, filename) is None:
                os.system("rm -f " + filename)

    def do(self):

        self.create_tmp_directory()

        if self._has_filename() is True:
            outfile = os.path.join(self.temp_dir, "ca.po")
            os.system("bzr cat " + self.url + " > " + outfile)
        else:
            os.system("cd " + self.temp_dir + "&& bzr checkout --lightweight " + self.url)
            self._remove_non_translation_files()

        self.add_comments()
        self.build()

        self.remove_tmp_directory()
