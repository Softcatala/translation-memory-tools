#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018-2021 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import sys

if __name__ == '__main__':
    print('Create Weblate credentials')

    filename = os.path.join(sys.argv[1], 'weblate.yaml')
    f = open(filename, "w+")

    credentials = 0
    for i in range(1, 10):
        project = 'WEBLATE_PROJECT_{0}'.format(i)
        token = 'WEBLATE_TOKEN_{0}'.format(i)

        if token not in os.environ or project not in os.environ:
            break

        f.write("- {0}: \n".format(os.environ[project]))
        f.write("    auth-token: {0}\n".format(os.environ[token]))
        f.write("\n")
        credentials = credentials + 1

    f.close()
    print("Wrote file {0} with {1} credentials ".format(filename, credentials))

