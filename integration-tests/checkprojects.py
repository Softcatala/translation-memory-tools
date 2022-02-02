# -*- coding: utf-8 -*-
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
import urllib.request


class CheckProjects(object):

    def __init__(self, url):
        self.url = url

    def _clean_num_formatting(self, num):
        return num.replace(".", "")

    def _check_projects(self):
        PROJECT_ID = "tots"

        url = '{0}projects'
        url = url.format(self.url)
        urllib.request.urlretrieve(url, 'file.txt')
        with open('file.txt') as json_data:
            data = json.load(json_data)

        memories = data["memories"]
        for memory in memories:
            if memory['project_id'] != PROJECT_ID:
                continue

            self._assert_greater(len(memory['name']), 0)
            self._assert_greater(int(self._clean_num_formatting(memory['words'])), 0)
            self._assert_greater(len(memory['po_file_text']), 0)
            self._assert_greater(len(memory['po_file_link']), 0)
            self._assert_greater(len(memory['tmx_file_text']), 0)
            self._assert_greater(len(memory['tmx_file_link']), 0)
            return

        raise Exception(f"'{PROJECT_ID}' project not found")
            
    def _assert_greater(self, actual, minimum):
        if minimum > actual:
            text = u'Expected {0} to be greater than minimum {1}'
            raise Exception(text.format(minimum, actual))

    def check(self):
        try:
            self._check_projects()
            return True
        except Exception as detail:
            print('Error checking projects: ' + str(detail))
            return False
