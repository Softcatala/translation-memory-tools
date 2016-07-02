# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 Jordi Mas i Hernandez <jmas@softcatala.org>
# Copyright (c) 2014 Leandro Regueiro Iglesias <leandro.regueiro@gmail.com>
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

import logging
import polib


class POFile(object):

    def __init__(self, filename):
        self.filename = filename

    def add_comment_to_all_entries(self, comment):
        try:
            input_po = polib.pofile(self.filename)

            for entry in input_po:
                if len(entry.tcomment) > 0:
                    entry.tcomment = u'{0}\n{1}'.format(comment, entry.tcomment)
                else:
                    entry.tcomment = comment

            input_po.save(self.filename)
        except Exception:
            logging.error("POFile.add_comment_to_all_entries " + self.filename)


    def add_msgctxt_to_duplicates(self):
        logging.debug("POFile.add_msgctxt_to_duplicates for " + self.filename)

        try:
            input_po = polib.pofile(self.filename)
            msgids = dict()

            cnt = 0
            for entry in input_po:
                if entry.msgid in msgids:
                    entry.msgctxt = str(cnt)
                else:
                    msgids[entry.msgid] = True

                cnt = cnt +1
            input_po.save(self.filename)
        except Exception as e:
            print(e)
            logging.error("POFile.add_msgctxt_to_duplicates " + self.filename)
    def calculate_localized_string_checksum(self, checksum):
        try:
            poFile = polib.pofile(self.filename)
            for entry in poFile:
                # hashlib.sha1 isn't expecting a unicode object, but rather a
                # sequence of bytes in a str object
                checksum.update(entry.msgstr.encode('utf-8'))
        except Exception:
            logging.error("POFile.get_checksum exception " + self.filename)

    def get_statistics(self):
        words = 0

        try:
            poFile = polib.pofile(self.filename)
            for entry in poFile:
                string_words = entry.msgstr.split(' ')
                words += len(string_words)
        except Exception:
            logging.error("POFile.get_statistics exception " + self.filename)
        finally:
            return words

    def _remove_untranslated_strings(self):
        try:
            input_po = polib.pofile(self.filename)

            for entry in input_po:
                if entry.msgid == entry.msgstr:
                    input_po.remove(entry)

            input_po.save(self.filename)
        except Exception:
            logging.error("POFile._remove_untranslated_string " + self.filename)

