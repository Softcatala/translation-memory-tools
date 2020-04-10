# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import re

from .fileset import FileSet
from .gitfileset import GitFileSet
from .crawler import Crawler


class GitWebFileSet(FileSet):
    """
        Reads a list of projects from a GitWeb server by using crawling
         and then downloads the projects.
    """

    def set_pattern(self, pattern):
        self.pattern = pattern

    def set_project(self, project):
        self.project = project

    def expand_dynamic(self):
        crawler = Crawler(self.url)
        crawler.run()
        links = crawler.get_all_links()

        git_urls = {}
        # Try to get the git clone URL from the web viewer
        git_clone_domain = re.match('.*?(.*?)gitweb.*?', self.url).group(1)
        git_clone_url = '{0}{1}/'.format(git_clone_domain, 'git')

        for link in links:
            # Url have the format http://git.lxde.org/gitweb/?p=lxde/lxqt-config-randr.git;a=tree
            match = re.match('.*?p=(.*?);.*?', link)
            if match:
                name = match.group(1)
                git_urls[name] = git_clone_url + name

        # The Gerrit project has a single fileset assigned (this)
        # We empty the fileset and add dynamically the ones referenced by Gerrit
        self.project.filesets = []

        for project in git_urls.keys():
            fileset_name = project
            url = git_urls[project]

            fileset = GitFileSet(self.project_name, fileset_name, url, '')
            fileset.set_pattern('.*?ca.po')
            logging.debug("Gitweb adding {0}-{1}".format(self.project_name, name))
            self.project.add_fileset(fileset)

        self.project.report_errors = False
