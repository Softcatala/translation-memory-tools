# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import logging
import urllib
import urllib.parse
import urllib.request
from urllib.parse import urlparse
from html.parser import HTMLParser

from .fileset import FileSet
from .transifexfileset import TransifexFileSet


class OptionsExtractor(HTMLParser):
    """
    Customized HTMLParser that extracts options values from a Fedora page
    There are two kinds of pages:
        * Hub pages: https://www.transifex.com/django/django/language/ca/
        * Organization pages: https://www.transifex.com/organization/xfce
            * These are paginated and have the concept of 'next page'
    """

    def __init__(self, base_url, project):
        HTMLParser.__init__(self)
        self.base_url = base_url
        self.options = []
        self.next_page = None
        self.project = project

    def get_next_page(self):
        return self.next_page

    def get_options(self):
        return self.options

    def get_project_name_from_ahref(self, url):
        # Sample URL https://www.transifex.com/django/public/
        # where Subpath[1]= 'django'
        path = urlparse(self.base_url).path
        subpaths = path.split("/")
        prefix = "/{0}/".format(subpaths[1])

        if not url.startswith(prefix):
            return None

        url = url[len(prefix) :]
        idx = url.find("/")
        if idx == -1:
            return None

        return url[:idx]

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attrs = dict(attrs)

        if "href" in attrs:
            url = attrs["href"]
            if url is not None:
                if "class" in attrs:
                    klass = attrs["class"]
                else:
                    klass = None

                if klass == "next":
                    self.next_page = url
                else:
                    name = self.get_project_name_from_ahref(url)
                    if name is not None and name not in self.options:
                        self.options.append(name)


class Page(object):
    """Represents a downloaded web page and its content"""

    def __init__(self, url, project):
        self.content = None
        self.url = url
        self.project = project
        self.next_page = None
        self.options = []
        self.base_url = self._get_base_url(url)
        self._download_page()
        self._process_options()

    def _get_base_url(self, url):
        u = urlparse(url)
        return u.geturl()

    def _download_page(self):
        request = urllib.request.Request(self.url)
        handle = urllib.request.build_opener()
        self.content = str(handle.open(request).read(), "utf-8", errors="replace")

    def _process_options(self):
        parser = OptionsExtractor(self.url, self.project)
        parser.feed(self.content)
        parser.close()
        self.options = parser.get_options()
        self.next_page = parser.get_next_page()

    def get_all_options(self):
        return self.options

    def get_next_page(self):
        return self.next_page


class TransifexHubFileSet(FileSet):
    def set_project(self, project):
        self.project = project

    def _clean_string(self, result):
        result = result.replace(" ", "-")
        result = result.strip()
        result = result.lower()
        return result

    def expand_dynamic(self):
        try:
            # This project has a single fileset assigned (this)
            # We empty the fileset and add dynamically the ones referenced by Transifex
            self.project.filesets = []
            options = []
            url = self.url

            while url is not None:
                page = Page(url, self.project.name.lower())
                for option in page.get_all_options():
                    options.append(option)
                url = page.get_next_page()
                if url is not None:
                    url = self.url + url

            if len(options) == 0:
                logging.info(
                    "TransifexHubFileSet.expand_dynamic. Unable not find any project to add"
                )

            for option in options:
                url = self.url
                url = url + self._clean_string(option)
                fileset = TransifexFileSet(
                    self.project_name, self.project_id, option, url, "", self
                )
                self.project.add_fileset(fileset)

            # All the new filesets have been added re-process project now
            self.project.report_errors = False
        except Exception as detail:
            print(detail)
