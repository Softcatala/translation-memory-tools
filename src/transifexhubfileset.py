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

from fileset import FileSet
from findfiles import FindFiles
from urlparse import urlparse
from HTMLParser import HTMLParser
from transifexfileset import TransifexFileSet

import urllib2
import urlparse
import os
import logging

class OptionsExtractor(HTMLParser):
    """Customized HTMLParser that extracts options values from a form"""

    def __init__(self, base_url):
        HTMLParser.__init__(self)
        self.base_url = base_url
        self.options = []
       
    def get_options(self):
        return self.options 
  
    def get_project_name(self, url):
        prefix = '/ajax/projects/p/'
        
        if url.startswith(prefix) is False:
            return None

        url = url[len(prefix):]
        idx = url.find('/')
        if (idx == -1):
            return None

        return url[:idx]


    def handle_starttag(self, tag, attrs):

        if tag == 'tr':
            attrs = dict(attrs)
            if 'data-actions-url' in attrs:
                url = attrs['data-actions-url']
                print "data-actions-url:" + url
                if url is not None:
                    name = self.get_project_name(url)
                    if name is not None and name not in self.options:
                        self.options.append(name)
            
class Page:
    """Represents a downloaded web page and its content"""

    def __init__(self, url):
        self.content = None
        self.url = url
        self.options = []
        self.base_url = self._get_base_url(url)
        self._download_page()
        self._process_options()

    def _get_base_url(self, url):
        u = urlparse.urlparse(url)
        return u.geturl()

    def _download_page(self):
        request = urllib2.Request(self.url)
        handle = urllib2.build_opener()

        self.content = unicode(
            handle.open(request).read(),
            'utf-8',
            errors='replace'
        )

    def _process_options(self):
        parser = OptionsExtractor(self.url)
        parser.feed(self.content)
        parser.close()
        self.options = parser.get_options()

    def get_all_options(self):
        return self.options


class TransifexHubFileSet(FileSet):
    
    def set_project(self, project):
        self.project = project

    def _clean_string(self, result):

        result = result.replace(' ', '-')
        result = result.strip()
        result = result.lower()
        return result

    def do(self):

        transifex_url = "https://www.transifex.com/projects/p/"       
            
        try:

            # This project has a single fileset assigned (this)
            # We empty the fileset and add dynamically the ones referenced by Gerrit
            self.project.filesets = []
            page = Page(self.url)
            options = page.get_all_options()

            if len(options) == 0:
                logging.info('TransifexHubFileSet.Do. Unable not find any project to add')

            for option in options:
                url =  transifex_url
                url =  url + self._clean_string(option)
                fileset = TransifexFileSet(self.project_name, option, url, '')
                self.project.add(fileset)

            # All the new filesets have been added re-process project now
            self.project.do()

        except Exception as detail:
            print(detail)

