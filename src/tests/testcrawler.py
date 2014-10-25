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

from crawler import Page
from os import path
import unittest


class FilePage(Page):

    def _download_page(self):
        """Reads a file from disk instead from http connection"""
        folder = path.dirname(path.realpath(__file__))
        f = open(path.join(folder, 'testcrawler.html'))
        self.content = unicode(f.read(), 'utf-8', errors='replace')
        f.close()


class TestPage(unittest.TestCase):

    def test_get_links(self):
        page = FilePage('http://translationproject.org/team/ca.html')
        links = page.get_all_links()
        print str(len(links))

        self.assertEquals(len(links), 432)
        url = 'http://translationproject.org/PO-files/ca/cpplib-4.8.0.ca.po'
        self.assertTrue(url in links)

if __name__ == '__main__':
    unittest.main()
