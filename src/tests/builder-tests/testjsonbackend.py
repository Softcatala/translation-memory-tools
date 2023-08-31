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

from builder.jsonbackend import JsonBackend, ProjectDTO
from os import path
import unittest


class TestJsonBackend(unittest.TestCase):
    def _validate_mozilla_project_mozilla_fileset(self, fileset):
        url = "http://pootle.softcatala.org/ca/mozilla/export/zip"
        self.assertEquals(fileset.name, "mozilla")
        self.assertEquals(fileset.url, url)
        self.assertEquals(fileset.type, "compressed")
        self.assertEquals(fileset.pattern, "ca.po")
        self.assertEquals(fileset.retrieval_pattern, "https://.*?/ca/.*?")
        self.assertEquals(fileset.duplicates, "msgctxt")
        self._validate_mozilla_project_conversor(fileset.conversor_setup)
        return

    def _validate_mozilla_project_conversor(self, conversor):
        self.assertEquals(conversor.type, "string")
        self.assertEquals(conversor.verb, "add")
        self.assertEquals(conversor.command, " --encoding=utf-8")
        return

    def _validate_firefox_fileset(self, fileset):
        self.assertTrue(fileset.po_preprocessing)
        return

    def _validate_mozilla_project(self, project):
        url = "http://www.softcatala.org/wiki/Projectes/Mozilla"
        self.assertEquals(project.name, "Mozilla")
        self.assertEquals(project.project_id, "mozilla")
        self.assertEquals(project.license, "Propietària")
        self.assertEquals(project.quality_report, False)
        self.assertEquals(project.filename, "mozilla-tm.po")
        self.assertEquals(project.projectweb, url)
        self.assertEquals(len(project.filesets), 3)
        self._validate_mozilla_project_mozilla_fileset(project.filesets[0])
        self._validate_firefox_fileset(project.filesets[1])
        return

    def test_processFileSet(self):
        projects_dir = path.dirname(path.realpath(__file__))
        projects_dir += "/data/projects"
        json = JsonBackend(projects_dir)
        json.load()

        self.assertEquals(len(json.projects), 2)
        for project in json.projects:
            if project.name == "Mozilla":
                mozilla = project

        self._validate_mozilla_project(mozilla)

    def test_from_name_to_project_id(self):
        project = ProjectDTO("One Name")
        self.assertEquals(project.project_id, "one_name")

    def test_from_name_to_project_id(self):
        project = ProjectDTO("One's Name")
        self.assertEquals("ones_name-tm.po", project.filename)


if __name__ == "__main__":
    unittest.main()
