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

import sys
import unittest

sys.path.append('../src/')

from bazaarfileset import BazaarFileSet


class TestBazaarFileSet(unittest.TestCase):

    def test_has_filename_filename(self):
        bazaar = BazaarFileSet('project none',
            'filsetname',
            'lp:~mailman-l10n-ca/mailman.po',
            'none.po')
        self.assertTrue(bazaar._has_filename())

    def test_has_filename_path(self):
        bazaar = BazaarFileSet('project none', 'filesetname',
                               'lp:~mailman-l10n-ca/', 'none.po')
        self.assertFalse(bazaar._has_filename())


if __name__ == '__main__':
    unittest.main()
