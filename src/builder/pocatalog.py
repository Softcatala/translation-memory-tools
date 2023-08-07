# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import shutil
import tempfile


class POCatalog(object):
    """Encapsulates the access to PO catalogs using msgattrib and
    and msgcat commands"""

    def __init__(self, filename):
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    def add_pofile(self, pofile):
        if os.path.isfile(self.filename):
            backup = next(tempfile._get_candidate_names())
            shutil.copy(self.filename, backup)
            cmd = "msgcat -tutf-8 --use-first -o {0} {1} '{2}' 2> /dev/null"
            os.system(cmd.format(self.filename, backup, pofile))
            os.remove(backup)
        else:
            if os.path.isfile(pofile):
                shutil.copy(pofile, self.filename)

    def cleanup(self):
        if os.path.isfile(self.filename) is False:
            return

        backup = next(tempfile._get_candidate_names())
        shutil.copy(self.filename, backup)
        cmd = (
            "msgattrib {0} --no-fuzzy --no-obsolete --translated > {1}" " 2> /dev/null"
        )
        os.system(cmd.format(backup, self.filename))
        os.remove(backup)
