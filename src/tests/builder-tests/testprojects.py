# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from unittest import TestCase, mock
from builder.projects import Projects

class TestProjects(TestCase):

    def test_get_db_name(self):
        projects = Projects(False)

        with mock.patch.dict('os.environ', {'DB3_PATH': ''}):
            self.assertEquals('statistics.db3', projects._get_db_name())

    def test_get_db_name_env(self):
        projects = Projects(False)

        with mock.patch.dict('os.environ', {'DB3_PATH': '/path/'}):
            self.assertEquals('/path/statistics.db3', projects._get_db_name())


if __name__ == '__main__':
    unittest.main()
