# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import urllib.request
import os


class CheckQualityReports(object):
    def __init__(self, url):
        self.url = url

    def _check_quality_reports_biggest_size(self):
        url = "{0}projects"
        url = url.format(self.url)
        urllib.request.urlretrieve(url, "file.txt")
        with open("file.txt") as json_data:
            data = json.load(json_data)

        memories = data["memories"]
        biggest = 0
        for memory in memories:
            link = memory["quality_file_link"]
            if len(link) == 0:
                continue

            filename = os.path.basename(link)
            full_filename = os.path.join("quality/", filename)
            size = os.stat(full_filename).st_size
            if size > biggest:
                biggest = size

        MIN_REPORT_SIZE = 10000
        if biggest < MIN_REPORT_SIZE:
            text = f"Expected at least one quality report to be bigger than {MIN_REPORT_SIZE} bytes, larger report was {biggest} bytes"
            raise Exception(text)

    def check(self):
        try:
            self._check_quality_reports_biggest_size()
            return True
        except Exception as detail:
            print("Error checking quality reports: " + str(detail))
            return False
