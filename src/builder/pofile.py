# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import polib
import shutil


class POFile(object):

    def __init__(self, filename):
        self.filename = filename

    def add_comment_to_all_entries(self, comment):

        try:

            bakfile = self.filename + '.bak'

            shutil.copy(self.filename, bakfile)

            input_po = polib.pofile(bakfile)

            for entry in input_po:
                if len(entry.tcomment) > 0:
                    entry.tcomment = u'{0}\n{1}'.format(comment, entry.tcomment)
                else:
                    entry.tcomment = comment

            input_po.save(self.filename)

        except Exception as detail:
            print("POFile.add_comment_to_all_entries " + self.filename)
            print(detail)

    def calculate_localized_string_checksum(self, checksum):

        try:

            poFile = polib.pofile(self.filename)
            for entry in poFile:
                # hashlib.sha1 isn't expecting a unicode object, but rather a
                # sequence of bytes in a str object
                checksum.update(entry.msgstr.encode('utf-8'))

        except Exception as detail:
            print("POFile.get_checksum exception " + self.filename)
            print(detail)

    def get_statistics(self):

        words = 0

        try:

            poFile = polib.pofile(self.filename)
            for entry in poFile:
                string_words = entry.msgstr.split(' ')
                words += len(string_words)

        except Exception as detail:
            print("POFile.get_statistics exception " + self.filename)
            print(detail)

        finally:
            return words
