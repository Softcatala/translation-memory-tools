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

import re
import logging

from .crawler import Crawler
from .gitfileset import GitFileSet
from .fileset import FileSet


class CGitFileSet(FileSet):

    HTTPS_PROTOCOL = 'https://'
    GIT_PROTOCOL = 'git://'
    DISCARD_NON_GIT_URI = '(.*/tree|.*/log)'
    FILESET_PATTERN = '.*?ca.po'

    def set_project(self, project):
        self.project = project

    def set_pattern(self, pattern):
        self.pattern = pattern

    def _get_download_links(self, links, directory):
        unique_links = set()
        for link in links:
            if re.match(self.DISCARD_NON_GIT_URI, link):
                continue
            if re.match(self.pattern, link):
                if link not in unique_links:
                    unique_links.add(link)

        return unique_links

    def _get_fileset_from_url(self, url):
        url = url.rstrip('/')
        idx = url.rfind('/')
        if idx == -1:
            return None

        return url[idx + 1:]

    def do(self):
        crawler = Crawler(self.url)
        crawler.run()
        links = crawler.get_all_links()
        unique_links = self._get_download_links(links, self.temp_dir)

        # This project has a single fileset assigned (this)
        # We empty the fileset and add dynamically the ones got by the crawler
        self.project.filesets = []

        try:

            for link in unique_links:
                name = self._get_fileset_from_url(link)
                if link[:len(self.HTTPS_PROTOCOL)] == self.HTTPS_PROTOCOL:
                    link = self.GIT_PROTOCOL + link[len(self.HTTPS_PROTOCOL):]
                fileset = GitFileSet(self.project_name, name, link, '')
                fileset.set_pattern(self.FILESET_PATTERN)
                self.project.add_fileset(fileset)

            # All the new filesets have been added re-process project now
            self.project.report_errors = False
            self.project.do()
            self.build()
        except Exception as detail:
            logging.error("CGitFileSet.do exception " + str(detail))
