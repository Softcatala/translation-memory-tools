#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import json
from usage import Usage


class Stats(object):
    def _read_index_json(self):
        with open("index.json", "r") as fh_json:
            d = json.load(fh_json)
        return d

    def str_to_int(self, string):
        return int(string.replace(".", ""))

    def get_json(self, date_requested):
        usage = Usage()
        calls = usage.get_stats(date_requested)
        index_json = self._read_index_json()

        results = {}
        results["total_words"] = self.str_to_int(index_json["words"])
        results["projects"] = self.str_to_int(index_json["projects"])
        results["searches"] = calls
        return json.dumps(results, indent=4, separators=(",", ": "))
