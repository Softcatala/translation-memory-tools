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

from builder.jsonbackend import JsonBackend
from os import path
import unittest


class TestJsonBackend(unittest.TestCase):

    def _validate_mozilla_project_mozilla_fileset(self, fileset):
        url = 'http://pootle.softcatala.org/ca/mozilla/export/zip'
        self.assertEquals(fileset.name, 'mozilla')
        self.assertEquals(fileset.url, url)
        self.assertEquals(fileset.type, 'compressed')
        self.assertEquals(fileset.excluded, 'region.properties.po')
        self.assertEquals(fileset.excluded, 'region.properties.po')
        self.assertEquals(fileset.pattern, 'http://.*?/ca/.*?')
        return

    def _validate_mozilla_project(self, project):
        url = 'http://www.softcatala.org/wiki/Projectes/Mozilla'
        self.assertEquals(project.name, 'Mozilla')
        self.assertEquals(project.filename, 'mozilla-tm.po')
        self.assertEquals(project.projectweb, url)
        self.assertEquals(len(project.filesets), 3)
        self._validate_mozilla_project_mozilla_fileset(project.filesets[0])
        return

    def test_processFileSet(self):

        folder = path.dirname(path.realpath(__file__))
        json = JsonBackend(path.join(folder, 'testjsonbackend.json'))
        json.load()

        self.assertEquals(len(json.projects), 2)
        self._validate_mozilla_project(json.projects[0])


if __name__ == '__main__':
    unittest.main()
