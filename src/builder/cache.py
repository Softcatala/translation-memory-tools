# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import time


class Cache:
    def __init__(self, directory="output/cache"):
        self.directory = directory
        self._create_dir_if_needed()

    def _create_dir_if_needed(self):
        if os.path.exists(self.directory) is False:
            os.makedirs(self.directory)

    def _get_cache_filename(self, url):
        del_chars = "".join(c for c in map(chr, range(256)) if not c.isalnum())
        del_map = str.maketrans("", "", del_chars)
        filename = url.translate(del_map)
        return filename

    def _get_file_age_in_hours(self, filename):
        current_time = time.time()
        file_time = os.path.getctime(filename)
        hours_old = (current_time - file_time) / 3600
        return hours_old

    def get(self, url):
        TIME_TO_EXPIRE_HOURS = 24
        filename = os.path.join(self.directory, self._get_cache_filename(url))

        if os.path.exists(filename) is False:
            return None

        if self._get_file_age_in_hours(filename) > TIME_TO_EXPIRE_HOURS:
            return None

        with open(filename, "r") as stream:
            content = stream.read()
            return content

    def set(self, url, content):
        filename = os.path.join(self.directory, self._get_cache_filename(url))

        with open(filename, "w") as stream:
            content = stream.write(content)
