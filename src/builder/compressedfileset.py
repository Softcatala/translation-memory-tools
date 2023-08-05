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

import logging
import os
import re
from .downloadfile import DownloadFile
from .fileset import FileSet
from .findfiles import FindFiles

class CompressedFileSet(FileSet):

    def _uncompress(self, filename, report_error):
        CompressedFileSet.uncompress(filename, report_error, self.temp_dir)

    def uncompress(filename, report_error, temp_dir):
        if filename.endswith('.zip'):
            os.system('unzip {0} -d {1}'.format(filename, temp_dir))
        elif filename.endswith('tar.gz'):
            cmd = 'tar -xvf {0} -C {1}'.format(
                filename,
                temp_dir
            )
            os.system(cmd)
        elif filename.endswith('.gz'):
            # We are assuming that the .gz file will contain a single PO
            cmd = 'gunzip {0} -c > {1}/ca.po'.format(
                filename,
                temp_dir
            )
            os.system(cmd)
        elif filename.endswith('tar.xz'):
            cmd = 'tar -Jxf {0} -C {1}'.format(filename, temp_dir)
            os.system(cmd)
        else:
            if report_error is True:
                msg = 'Unsupported file extension for filename: {0}'
                logging.error(msg.format(filename))

    def set_pattern(self, pattern):
        self.pattern = pattern

    def clean_up_after_convert(self):
        self._remove_non_translation_files()

    def _remove_non_translation_files(self):
        if self.pattern is None or len(self.pattern) == 0:
            return

        findFiles = FindFiles()

        for filename in findFiles.find_recursive(self.temp_dir, '*'):

            if re.match(self.pattern, filename) is None and \
                    os.path.exists(filename):
                os.remove(filename)
                print(filename)

    def do(self):
        # Download po files
        download = DownloadFile()
        download.get_file(self.url, self.filename)

        self._uncompress(self.filename, True)
        self.build()

        if os.path.exists(self.filename):
            os.remove(self.filename)
