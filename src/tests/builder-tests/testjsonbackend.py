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
        self.assertEqual(fileset.name, "mozilla")
        self.assertEqual(fileset.url, url)
        self.assertEqual(fileset.type, "compressed")
        self.assertEqual(fileset.pattern, "ca.po")
        self.assertEqual(fileset.retrieval_pattern, "https://.*?/ca/.*?")
        self.assertEqual(fileset.duplicates, "msgctxt")
        self._validate_mozilla_project_conversor(fileset.conversor_setup)

    def _validate_mozilla_project_conversor(self, conversor):
        self.assertEqual(conversor.type, "string")
        self.assertEqual(conversor.verb, "add")
        self.assertEqual(conversor.command, " --encoding=utf-8")

    def _validate_firefox_fileset(self, fileset):
        self.assertTrue(fileset.po_preprocessing)

    def _validate_mozilla_project(self, project):
        url = "http://www.softcatala.org/wiki/Projectes/Mozilla"
        self.assertEqual(project.name, "Mozilla")
        self.assertEqual(project.project_id, "mozilla")
        self.assertEqual(project.license, "Propietària")
        self.assertEqual(project.quality_report, False)
        self.assertEqual(project.filename, "mozilla-tm.po")
        self.assertEqual(project.projectweb, url)
        self.assertEqual(len(project.filesets), 3)
        self._validate_mozilla_project_mozilla_fileset(project.filesets[0])
        self._validate_firefox_fileset(project.filesets[1])

    def test_processFileSet(self):
        projects_dir = path.dirname(path.realpath(__file__))
        projects_dir += "/data/projects"
        json = JsonBackend(projects_dir)
        json.load()

        self.assertEqual(len(json.projects), 2)
        for project in json.projects:
            if project.name == "Mozilla":
                mozilla = project

        self._validate_mozilla_project(mozilla)

    def test_from_name_to_project_id(self):
        project = ProjectDTO("One Name")
        self.assertEqual(project.project_id, "one_name")

    def test_from_name_to_project_filename(self):
        project = ProjectDTO("One's Name")
        self.assertEqual("ones_name-tm.po", project.filename)


if __name__ == "__main__":
    unittest.main()
