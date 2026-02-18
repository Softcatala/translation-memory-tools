# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import urllib.request
import urllib.parse
import json
import logging
import os
import yaml

from .fileset import FileSet
from .downloadfile import DownloadFile


class ZanataFileSet(FileSet):
    username = None
    auth = None
    TIMEOUT = 15

    def _set_auth_api_token(self):
        try:
            with open("../cfg/credentials/zanata.yaml", "r") as stream:
                values = yaml.load(stream, Loader=yaml.FullLoader)
                for value in values:
                    if self.project_name not in value:
                        continue

                    self.username = value[self.project_name]["username"]
                    self.auth = value[self.project_name]["auth-token"]

            if self.username is None or self.auth is None:
                msg = "ZanataFileSet._set_auth_api_token: No user or auth token"
                logging.error(msg)

        except Exception as detail:
            msg = "ZanataFileSet._set_auth_api_token: {0}".format(str(detail))
            logging.error(msg)

    def _get_projects_ids(self):
        url = urllib.parse.urljoin(self.url, "/rest/projects")
        headers = {"accept": "application/json"}

        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=self.TIMEOUT)
        response_text = response.read().decode(
            response.info().get_param("charset") or "utf-8"
        )
        projects = json.loads(response_text)
        ids = []
        for project_dict in projects:
            ids.append(project_dict["id"])

        logging.debug(f"ZanataFileSet._get_projects_ids returns {len(ids)} ids")
        return ids

    # Try to get first only the master (latest) version. It prevents downloading old translations
    # If this does not work, download the full memory
    def _get_tmx_file(self, project_id):
        if self._get_single_tmx_file(
            project_id, "/rest/tm/projects/{0}/iterations/master?locale=ca", False
        ):
            return

        self._get_single_tmx_file(project_id, "/rest/tm/projects/{0}?locale=ca", True)

    def _get_single_tmx_file(self, project_id, base_url, report_error):
        req = base_url.format(project_id)
        url = urllib.parse.urljoin(self.url, req)
        headers = {"X-Auth-User": self.username, "X-Auth-Token": self.auth}

        try:
            filename = "{0}-ca.tmx".format(project_id)
            filename = os.path.join(self.temp_dir, filename)

            DownloadFile().get_file(url, filename, headers)
            return True

        except Exception as detail:
            if report_error:
                logging.error(
                    "ZanataFileSet._get_single_tmx_file {0} - error: {1}".format(
                        url, detail
                    )
                )

            return False

    def do(self):
        self._set_auth_api_token()
        project_ids = self._get_projects_ids()
        for project_id in project_ids:
            self._get_tmx_file(project_id)

        self.build()
