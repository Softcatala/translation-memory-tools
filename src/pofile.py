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
import polib


class POFile:

    def add_comment_to_all_entries(self, filename, comment):

        bakfile = filename + ".bak"

        os.system("cp " + filename + " " + bakfile)

        input_po = polib.pofile(bakfile)

        for entry in input_po:
            if len(entry.tcomment) > 0:
                entry.tcomment = comment + "\n" + entry.tcomment
            else:
                entry.tcomment = comment

        input_po.save(filename)
