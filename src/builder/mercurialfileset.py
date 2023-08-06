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
import shutil

from .fileset import FileSet


class MercurialFileSet(FileSet):

    hg_dir = '_hg'

    def _get_filename(self):
        filename = self.url.split('/')[-1]
        return filename

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
