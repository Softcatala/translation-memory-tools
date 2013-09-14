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

from fileset import FileSet, FindFiles
from urlparse import urlparse


class TransifexFileSet(FileSet):

    def remove_non_translation_only_files(self):

        findFiles = FindFiles()

        for filename in findFiles.find(self.temp_dir, '*'):
            if (filename.endswith('en.po') or filename.endswith('en.ts')):
                os.system("rm -f " + filename)

    def do(self):

        prevdir = os.getcwd()

        os.system("rm -r -f " + self.temp_dir)
        os.system("mkdir " + self.temp_dir)
        os.chdir(self.temp_dir)

        url = urlparse(self.url)
        uri = url.scheme + "://" + url.netloc
        os.system("tx init --host " + uri)
        os.system("tx set --auto-remote " + self.url)

        # To be able to process files with no English source (.strings, .xml,
        # etc) we pull the English files too and then we delete the ones that
        # include source and target
        os.system("tx pull -f -lca,en")
        os.chdir(prevdir)
        self.remove_non_translation_only_files()

        self.convert_ts_files_to_po()
        self.convert_string_files_to_po()
        self.add_comments()
        self.build()

        os.system("rm -r -f " + self.temp_dir)
