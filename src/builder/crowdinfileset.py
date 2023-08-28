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

import urllib.request
import urllib.parse
import json
import logging
import os
import yaml

from urllib.error import HTTPError
from .fileset import FileSet


class CrowdinFileSet(FileSet):
    TIMEOUT = 60  # The export time in the server may take some time
    token = None
    requests = 0

    def _get_auth_api_token(self):
        try:
            if self.token is not None:
                return self.token

            with open("../cfg/credentials/crowdin.yaml", "r") as stream:
                values = yaml.load(stream, Loader=yaml.FullLoader)
                self.token = values[0]["auth-token"]

            if self.token is None:
                msg = "CrowdinFileSet._get_auth_api_token: No auth token"
                logging.error(msg)

            return self.token

        except Exception as detail:
            msg = "CrowdinFileSet._get_auth_api_token: {0}".format(str(detail))
            logging.error(msg)

    def _api_json_post(self, url, data):
        req = urllib.request.Request(url, headers=self._get_headers())
        jsondata = json.dumps(data)
        jsondataasbytes = jsondata.encode("utf-8")
        response = urllib.request.urlopen(req, jsondataasbytes, timeout=self.TIMEOUT)
        response_text = response.read().decode(
            response.info().get_param("charset") or "utf-8"
        )
        return json.loads(response_text)

    def _get_headers(self):
        token = self._get_auth_api_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
        }

        return headers

    def _get_file(self, url, filename):
        try:
            filename = os.path.join(self.temp_dir, filename)
            req = urllib.request.Request(url)

            msg = "Download file {0}".format(filename)
            logging.info(msg)

            with urllib.request.urlopen(req, timeout=self.TIMEOUT) as infile, open(
                filename, "wb"
            ) as output:
                output.write(infile.read())
                output.close()
                return True

        except HTTPError as detail:
            if detail.code == 404:
                logging.info(
                    "CrowdinFileSet._get_file {0} - info: {1}".format(url, detail)
                )
            else:
                logging.error(
                    "CrowdinFileSet._get_file {0} - error: {1}".format(url, detail)
                )
            return False

        except Exception as detail:
            logging.error(
                "CrowdinFileSet._get_file {0} - error: {1}".format(url, detail)
            )
            return False

    def do(self):
        data = {"targetLanguageId": "ca", "format": "xliff"}
        result = self._api_json_post(f"{self.url}/translations/exports", data)

        url = result["data"]["url"]
        name = self.name.lower()
        self._get_file(url, f"{name}.xliff")
        self.build()
