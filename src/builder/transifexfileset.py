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
import urllib
import urllib.parse
import re

from .fileset import FileSet
from .findfiles import FindFiles


class TransifexFileSet(FileSet):

    pattern = None

    def set_pattern(self, pattern):
        self.pattern = pattern

    def _remove_non_translation_only_files(self):

        findFiles = FindFiles()

        for filename in findFiles.find(self.temp_dir, '*'):
            if filename.endswith('en.po') or filename.endswith('en.ts') or\
               filename.endswith('en_GB.po') or filename.endswith('en_GB.ts') or \
               filename.endswith('en_US.po') or filename.endswith('en_US.ts'):
                   os.remove(filename)

            if self.pattern is not None and \
               re.match(self.pattern, filename) is None and \
                    os.path.exists(filename):
                os.remove(filename)

    def do(self):
        prevdir = os.getcwd()
        os.chdir(self.temp_dir)

        url = urllib.parse.urlparse(self.url)
        uri = '{0}://{1}'.format(url.scheme, url.netloc)
        os.system('tx init --host {0}'.format(uri))
        os.system('tx set --auto-remote {0}'.format(self.url))

        # To be able to process files with no English source (.strings, .xml,
        # etc) we pull the English files too and then we delete the ones that
        # include source and target
        cmd = 'tx --traceback pull -f -s -lca,ca_ES,en,en_GB'
        if self.project_name.lower() == 'blender':
            cmd += ' --mode onlyreviewed'

        os.system(cmd)
        os.chdir(prevdir)
        self._remove_non_translation_only_files()

        self.build()
