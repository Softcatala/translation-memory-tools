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
import logging


class POCatalog(object):
    """Encapsulates the access to PO catalogs using msgattrib and
    and msgcat commands"""

    def __init__(self, filename):
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    def _log_error_file(self, filename):
        MAX_LINES = 10
        with open(filename, "r") as _file:
            for cnt, line in enumerate(_file, 1):
                logging.debug(f"error: {line.strip()}")
                if cnt >= MAX_LINES:
                    break

    def _run_command(self, cmd):
        with tempfile.NamedTemporaryFile() as tmp:
            error_fn = tmp.name

            file_time = os.stat(self.filename).st_mtime
            # msgcat and msgattrib do not return a specific error code when they are unable
            # to run. If they run successfully the date of the output file is always updated
            os.system(cmd + f" 2> {error_fn}")
            is_error = file_time == os.stat(self.filename).st_mtime
            if is_error:
                self._log_error_file(error_fn)

            return is_error

    def add_pofile(self, pofile):
        if os.path.isfile(self.filename):
            with tempfile.NamedTemporaryFile() as tmp:
                backup = tmp.name
                shutil.copy(self.filename, backup)
                cmd = f"msgcat -tutf-8 --use-first -o {self.filename} {backup} '{pofile}' 2> /dev/null"
                if self._run_command(cmd):
                    logging.debug(
                        f"POCatalog.add_pofile. Unable to add file '{pofile}' with msgcat"
                    )
        else:
            if os.path.isfile(pofile):
                shutil.copy(pofile, self.filename)

    def cleanup(self):
        if os.path.isfile(self.filename) is False:
            return

        with tempfile.NamedTemporaryFile() as tmp:
            backup = tmp.name
            shutil.copy(self.filename, backup)
            cmd = f"msgattrib {backup} --no-fuzzy --no-obsolete --translated > {self.filename} 2> /dev/null"
            if self._run_command(cmd):
                logging.debug(
                    f"POCatalog.cleanup. Unable to processs file '{self.filename}' with msgattrib"
                )
