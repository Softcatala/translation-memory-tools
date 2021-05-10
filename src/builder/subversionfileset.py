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

import os

from .fileset import FileSet


class SubversionFileSet(FileSet):

    def do(self):
        if len(self.filename) == 0:
            CMD = 'cd {0} && svn co --trust-server-cert --non-interactive {1} > /dev/null'
        else:
            # Single file checkout
            CMD = ('cd {0} && svn export --trust-server-cert '
                   '--non-interactive {1} > /dev/null')

        cmd = CMD.format(self.temp_dir, self.url)
        os.system(cmd)

        self.build()
