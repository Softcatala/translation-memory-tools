#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017-2021 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import json
import tempfile
import shutil
import logging

class LanguageTool():

    def __init__(self, config):
        self._config = config

    def generate_lt_report(self, lt_html_dir, json_file, file_report):
        subdir = "output/individual_pos/"
        curdir = os.getcwd()
        cwd = os.path.join(curdir, subdir)
        if cwd == json_file[:len(cwd)]:
            json_file = json_file[len(cwd):]
        elif subdir == json_file[:len(subdir)]:
            json_file = json_file[len(subdir):]

        cmd = 'cd {0} && python3 {1}/lt-json-to-html.py -i "{2}" -o "{3}"'.format(
               subdir, os.path.join(curdir, lt_html_dir), json_file, file_report)

        os.system(cmd)

    def run_lt(self, lt, txt_file, json_file):
        lt_server = os.environ.get('LT_SERVER', 'http://localhost:7001/v2/check')
        cmd = lt['command'].format(lt['enabled-rules'], lt['disabled-rules'], lt['disabled-categories'],
              txt_file, lt_server, json_file)
        os.system(cmd)

    def _get_lt_version(self):
        data_file = None
        TEXT_FILE = 'version.txt'
        JSON_FILE = 'version.json'

        try:
            dirpath = tempfile.mkdtemp()
            lt = self._config

            text_filename = os.path.join(dirpath, TEXT_FILE)
            with open(text_filename, "w") as outfile:
                outfile.write('Hola')

            json_filename = os.path.join(dirpath, JSON_FILE)
            self.run_lt(lt, text_filename, json_filename)

            with open(json_filename, "r") as data_file:
                data = json.load(data_file)

            software = data['software']
            version = '{0} {1}'.format(software['name'], software['version'])
            shutil.rmtree(dirpath)
            return version
        except Exception as e:
            logging.error("_get_lt_version.Error {0}".format(str(e)))
            return "LanguageTool (versió desconeguda)"

