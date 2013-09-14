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


class BazaarFileSet(FileSet):

    def do(self):

        os.system("rm -r -f " + self.temp_dir)
        os.system("mkdir " + self.temp_dir)
        os.system("cd " + self.temp_dir)
        os.system("bzr cat " + self.url + " > ca.po")

        self.uncompress()
        self.convert_ts_files_to_po()
        self.add_comments()
        self.build()

        os.system("rm -f ca.po")
        os.system("rm -r -f " + self.temp_dir)
