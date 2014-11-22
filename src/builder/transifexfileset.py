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
from urlparse import urlparse

from fileset import FileSet
from findfiles import FindFiles


class TransifexFileSet(FileSet):

    def _remove_non_translation_only_files(self):
        findFiles = FindFiles()

        for filename in findFiles.find(self.temp_dir, '*'):
            if filename.endswith('en.po') or filename.endswith('en.ts'):
                os.remove(filename)

    def do(self):
        prevdir = os.getcwd()

        self.create_tmp_directory()
        os.chdir(self.temp_dir)

        url = urlparse(self.url)
        uri = '{0}://{1}'.format(url.scheme, url.netloc)
        os.system('tx init --host {0}'.format(uri))
        os.system('tx set --auto-remote {0}'.format(self.url))

        # To be able to process files with no English source (.strings, .xml,
        # etc) we pull the English files too and then we delete the ones that
        # include source and target
        os.system('tx pull -f -lca,ca_ES,en')
        os.chdir(prevdir)
        self._remove_non_translation_only_files()

        self.build()
        #self.remove_tmp_directory()
