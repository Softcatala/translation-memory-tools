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

from fileset import FileSet
from findfiles import FindFiles

import os
import logging
import re


class GitFileSet(FileSet):

    def __init__(self, project_name, name, url, filename):
        FileSet.__init__(self, project_name, name, url, filename)
        self.AndroidRemove = False

    def _get_filename(self):
        filename = self.url.split('/')[-1]
        return filename

    def _remove_non_translation_files_for_android(self):
        findFiles = FindFiles()

        for filename in findFiles.find(self.temp_dir, '*'):
            # Some Android projects contain there own po files like
            # https://android.googlesource.com/platform/ndk and they have
            # the name standard "ca.po"
            # The rest are produced by a2po then they have the pattern '-ca.po'
            if re.match('.*?ca.po', filename) is None:
                if os.path.exists(filename):
                    os.remove(filename)
            else:
                logging.debug("Keeping file:" + filename)

    def _php_conversion_for_moodle(self):

        findFiles = FindFiles()
        if len(findFiles.find(self.temp_dir, '*.php')) == 0:
            return

        GIT_DIRNAME = 'moodle-langpacks'
        OUT_DIRNAME = 'po-files'
        cmd = 'cd {0} && php2po -t {1}/en -i {1}/ca ' \
              '-o {2}'.format(self.temp_dir, GIT_DIRNAME, OUT_DIRNAME)
        os.system(cmd)

    def convert_android_resources_files_to_po(self):

        filename = self._get_filename()

        # See: https://pypi.python.org/pypi/android2po/1.2.0
        cmd = 'cd {0}/{1} && a2po init ca'.format(self.temp_dir, filename)
        os.system(cmd)

    def do(self):
        self.create_tmp_directory()

        os.system('cd {0} && git clone --depth=1 {1}'.format(
            self.temp_dir,
            self.url
        ))

        self._php_conversion_for_moodle()
        self.convert_android_resources_files_to_po()

        if self.AndroidRemove:
            self._remove_non_translation_files_for_android()

        self.add_comments()
        self.build()

        self.remove_tmp_directory()
