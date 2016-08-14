# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Jordi Mas i Hernandez <jmas@softcatala.org>
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
from .gitfileset import GitFileSet
from .convertfiles import ConvertFiles
from .findfiles import FindFiles


class XiaomiFileSet(FileSet):
    """
        Steps
            1. Download Catalan files
            2. Download English files (different source)
            3. Move English to Catalan subdir
            4. Create filesets dynamically for subdir
    """

    def do(self):
        project_name = 'xiaomi'
        filename = None
        catalan = GitFileSet(project_name, 'Catalan', self.url, filename)

        catalan.download()

        english = GitFileSet(project_name, 'English',
                            'https://github.com/iBotPeaches/MIUIAndroid_XML',
                             filename)

        english.download()

        cd = 'cd {0}/Catalan'.format(self.temp_dir)
        cmd = cd + ' && cp -r ../English/* .'.format(self.temp_dir)
        os.system(cmd)

        # Rename directories value-en to value
        cmd = cd + ' && find . -name values-en -type d -execdir mv {} values \;'
        os.system(cmd)

        findFiles = FindFiles()
        for filename in findFiles.find_dirs(self.temp_dir, '*.apk'):
            convert = ConvertFiles(filename, self.conversor_setup)
            convert.android_dir = "res"
            convert.convert()

        self.build()
