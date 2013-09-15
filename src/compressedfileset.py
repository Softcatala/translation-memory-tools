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
from fileset import FileSet
from downloadfile import DownloadFile


class CompressedFileSet(FileSet):

    def _uncompress(self):

        if (self.filename.endswith('.zip')):
            os.system("unzip " + self.filename + " -d " + self.temp_dir)
        elif (self.filename.endswith('tar.gz')):
            os.system("mkdir " + self.temp_dir)
            if len(self.pattern) > 0:
                os.system("tar -xvf " + self.filename + " -C " + self.temp_dir +
                          self.pattern)
            else:
                os.system("tar -xvf " + self.filename + " -C " + self.temp_dir)

        elif (self.filename.endswith('.gz')):
            os.system("mkdir " + self.temp_dir)
            # We are assuming that the .gz file will contain a single PO
            os.system("gunzip " + self.filename + " -c > " + self.temp_dir
                      + "/ca.po")
        elif (self.filename.endswith('.po') or self.filename.endswith('.ts')):
            os.system("mkdir " + self.temp_dir)
            os.system("cp " + self.filename + " " + self.temp_dir + "/" + self.filename)
        elif (self.filename.endswith('tar.xz')):
            os.system("mkdir " + self.temp_dir)
            os.system("tar -Jxf " + self.filename + " -C " + self.temp_dir)
        else:
            logging.error("Unsupported file extension for filename:" + self.filename)

    def set_pattern(self, pattern):
        self.pattern = pattern

    def do(self):

        self.create_tmp_directory()
        
        # Download po files
        download = DownloadFile()
        download.get_file(self.url, self.filename)

        self._uncompress()
        self.convert_ts_files_to_po()
        self.add_comments()
        self.build()

        os.system("rm -f " + self.filename)
        self.remove_tmp_directory()
