#!/usr/bin/env python2
#
# Copyright (c) 2013 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import urllib2
import urlparse
from Queue import Queue
from HTMLParser import HTMLParser


class LinkExtractor(HTMLParser):
    """Customized HTMLParser that extracts links"""

    def __init__(self, base_url):
        HTMLParser.__init__(self)
        self.base_url = base_url
        self.links = []

    def get_links(self):
        return self.links

    def handle_starttag(self, tag, attrs):

        if tag == "a":
            attrs = dict(attrs)
            link = attrs["href"]

            if link is not None:
                absolute = urlparse.urljoin(self.base_url, link)
                self.links.append(absolute)


class Page:
    """Represents a downloaded web page and its content"""

    def __init__(self, url):
        self.content = None
        self.url = url
        self.links = []
        self.base_url = self._get_base_url(url)
        self._download_page()
        self._process_links()

    def _get_base_url(self, url):
        u = urlparse.urlparse(url)
        return u.geturl()

    def _download_page(self):

        request = urllib2.Request(self.url)
        handle = urllib2.build_opener()

        self.content = unicode(handle.open(request).read(), "utf-8",
                               errors="replace")

    def _process_links(self):

        parser = LinkExtractor(self.url)
        parser.feed(self.content)
        parser.close()
        self.links = parser.get_links()

    def get_all_links(self):
        return self.links

    def get_child_pages_links(self):

        children = []
        for link in self.links:
            if link.startswith(self.base_url) is True:
                children.append(link)

        return children


class Crawler:
    """Crawls urls and gets the links to translations files"""

    def __init__(self, root):

        self.urls = Queue()
        self.urls.put(root)

    def run(self):

        url = self.urls.get()

        page = Page(url)
        links = page.get_all_links()

        return links
