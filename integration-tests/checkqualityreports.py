#!/usr/bin/env python2
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

import sys
sys.path.append('../src/')
import urllib
from builder.jsonbackend import JsonBackend


class CheckQualityReports(object):

    HTTP_STATUS_CODE_OK = 200
    HTTP_STATUS_CODE_NOT_FOUND = 404
    MIN_REPORT_LENGTH = 1400

    def __init__(self, site_url):
        self.site_url = site_url
        self.errors = 0

    def check_links(self, project):
        lt = '{0}quality/{1}.html'.format(self.site_url, project)
        self._check_link(lt)

    def _check_link(self, link):
        code = CheckQualityReports.HTTP_STATUS_CODE_NOT_FOUND
        length = 0
        try:
            rtr = urllib2.urlopen(link)
            code = rtr.getcode()
            length = len(rtr.read())
        except Exception:
            pass

        if code != CheckQualityReports.HTTP_STATUS_CODE_OK:
            self.errors += 1
            print('Link {0} returns {1}'.format(link, str(code)))
            return False

        if length < self.MIN_REPORT_LENGTH:
            self.errors += 1
            print('Link {0} content is only {1} bytes'.format(link,
                  str(length)))
            return False

        return True

    def check(self):
        """Reads the json and makes sure that for every project we have the
           expected quality reports
        """
        json = JsonBackend("../cfg/projects/")
        json.load()

        for project_dto in json.projects:
            if not project_dto.downloadable:
                continue

            self.check_links(project_dto.name.lower())
