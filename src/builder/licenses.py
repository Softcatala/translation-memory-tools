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

from os import path
import json


class Licenses():

    PROPIETARY = 'propietària'

    def __init__(self, filename = "../licenses/licenses.json"):
        self.filename = filename

    def _get_filename(self):
        projects_dir = path.dirname(path.realpath(__file__))
        return path.join(projects_dir, self.filename)

    def get_licenses_ids(self):
        licenses_ids = set()
        with open(self._get_filename()) as json_file:
            data = json.load(json_file)
            licenses = data['licenses']
            for license in licenses:
                licenses_ids.add(license['licenseId'])

        licenses_ids.add(self.PROPIETARY)
        return licenses_ids


    def get_licenses_name_and_link(self):
        results = {}
        with open(self._get_filename()) as json_file:
            data = json.load(json_file)
            licenses = data['licenses']
            for license in licenses:
                values = {}
                links = license.get('seeAlso')
                if links:
                    link = links[0]
                else:
                    link = None

                values['name'] = license.get('name')
                values['link'] = link
                licenseId = license['licenseId']
                results[licenseId] = values

        return results


    def are_compatible_licenses(self, source, target):
        if source != 'GPL-3.0-only':
            raise Exception("Unable to determine license compatibility on this source license")

        if target == 'GPL-2.0-only':
            return False

        return True
