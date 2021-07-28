#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Jordi Mas i Hernandez <jmas@softcatala.org>
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
from os.path import expanduser

if __name__ == '__main__':
    print('Create transifex credentials')

    home = expanduser("~")
    filename = os.path.join(home, '.transifexrc')
    f = open(filename, "w+")

    f.write("[https://www.transifex.com]\n")
    f.write("hostname = https://www.transifex.com\n")
    f.write("username = api\n")
    f.write("password = {0}\n".format(os.environ['TRANSIFEX_TOKEN']))
    f.close()
    print("Wrote file: " + filename)

