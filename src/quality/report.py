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

import datetime
import os
import pystache

class Report():

    def __init__(self):
        self._project_file = None

    def create_project_report(self, header_dir, lt_output, project_html, version):
        header_filename = os.path.join(header_dir, "header.mustache")
        report_filename = os.path.join(lt_output, project_html)

        ctx = {
            'date': datetime.date.today().strftime("%d/%m/%Y"),
            'languagetool': version,
        }

        self._process_template(header_filename, report_filename, ctx)
        self._project_file = open(report_filename, "a")

    def _process_template(self, template, filename, ctx):
        try:
            template = open(template, 'r').read()
            parsed = pystache.Renderer()
            s = parsed.render(template, ctx)

            f = open(filename, 'w')
            f.write(s)
            f.close()

        except Exception as e:
            print("_process_template. Error: {0}".format(e))

    def add_string_to_project_report(self, text):
        self._project_file.write(text + "\n")

    def add_file_to_project_report(self, filename):
        pology_file = open(filename, "r")
        self._project_file.write(pology_file.read())
        pology_file.close()

    def close(self):
        if self._project_file:
            self._project_file.close()
