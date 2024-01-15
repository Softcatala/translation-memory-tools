# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Jordi Mas i Hernandez <jmas@softcatala.org>
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
from .cache import Cache


class WeblateFileSet(FileSet):
    TIMEOUT = 15
    token = None
    cache = None
    cached = 0
    requests = 0

    def _get_auth_api_token(self):
        try:
            if self.token is not None:
                return self.token

            with open("../cfg/credentials/weblate.yaml", "r") as stream:
                values = yaml.load(stream, Loader=yaml.FullLoader)
                for value in values:
                    if self.url not in value.keys():
                        continue

                    self.token = value[self.url]["auth-token"]
                    break

            if self.token is None:
                msg = "WeblateFileSet._get_auth_api_token: No auth token"
                logging.error(msg)

            return self.token

        except Exception as detail:
            msg = "WeblateFileSet._get_auth_api_token: {0}".format(str(detail))
            logging.error(msg)

    def _api_json_call(self, url):
        if self.cache is None:
            self.cache = Cache()

        cached = self.cache.get(url)
        if cached:
            response_text = cached
            self.cached += 1
        else:
            req = urllib.request.Request(url, headers=self._get_headers())
            response = urllib.request.urlopen(req, timeout=self.TIMEOUT)
            response_text = response.read().decode(
                response.info().get_param("charset") or "utf-8"
            )
            self.cache.set(url, response_text)
            self.requests += 1

        return json.loads(response_text)

    def _has_catalan_language(self, url):
        languages = self._api_json_call(url)

        for language in languages:
            if language["code"] in ["ca", "ca_es"] and language["translated"] > 0:
                return True

        return False

    def _get_components(self, url):
        while url is not None:
            json = self._api_json_call(url)
            components = []

            for component_dict in json["results"]:
                slug = component_dict["slug"]
                components.append(slug)

            url = json["next"]

        return components

    def _get_headers(self):
        token = self._get_auth_api_token()
        headers = {"Authorization": f"Token {token}", "User-Agent": "Mozilla/5.0"}
        return headers

    def _get_projects_slugs(self):
        ids = {}
        url = urllib.parse.urljoin(self.url, "/api/projects/")
        while url is not None:
            projects = self._api_json_call(url)
            for project_dict in projects["results"]:
                slug = project_dict["slug"]
                if not self._has_catalan_language(project_dict["languages_url"]):
                    continue

                name_to_match = project_dict["name"].lower()
                if not self.is_retrieval_pattern(name_to_match):
                    continue

                components = self._get_components(project_dict["components_list_url"])
                ids[slug] = components

            url = projects["next"]

        return ids

    def _get_file(self, slug, component):
        # https://translate.fedoraproject.org/download/libvirt/libvirt/ca/?format=po
        fragment = f"/download/{slug}/{component}/ca/?format=po"
        url = urllib.parse.urljoin(self.url, fragment)

        try:
            filename = f"{slug}-{component}-ca.po"
            filename = os.path.join(self.temp_dir, filename)
            req = urllib.request.Request(url, headers=self._get_headers())

            msg = "Download file '{0}' to {1}".format(url, filename)
            logging.info(msg)

            infile = urllib.request.urlopen(req, timeout=self.TIMEOUT)
            output = open(filename, "wb")
            output.write(infile.read())
            output.close()
            return True

        except HTTPError as detail:
            if detail.code == 404:
                logging.info(
                    "WeblateFileSet._get_file {0} - info: {1}".format(url, detail)
                )
            else:
                logging.error(
                    "WeblateFileSet._get_file {0} - error: {1}".format(url, detail)
                )
            return False

        except Exception as detail:
            logging.error(
                "WeblateFileSet._get_file {0} - error: {1}".format(url, detail)
            )
            return False

    def do(self):
        slugs = self._get_projects_slugs()
        for slug in slugs:
            for component in slugs[slug]:
                self._get_file(slug, component)

        self.build()
        logging.info(
            f"WeblateFileSet {self.cached} cached API requests, done {self.requests}"
        )
