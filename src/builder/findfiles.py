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

import fnmatch
import os


class FindFiles(object):

    def find(self, directory, pattern):
        filelist = []

        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    filelist.append(filename)

        filelist.sort()
        return filelist

    def find_recursive(self, directory, pattern):
        filelist_set = set()
        dirs = self.find_dirs(directory, "*")
        for _dir in dirs:
            files = self.find(_dir, pattern)
            for f in files:
                filelist_set.add(f)

        filelist = list(filelist_set)
        filelist.sort()
        return filelist

    def find_dirs(self, directory, pattern):
        dirlist = []

        for root, dirs, files in os.walk(directory):
            for basename in dirs:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    dirlist.append(filename)

        dirlist.sort()
        return dirlist
