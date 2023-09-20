#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017-2021 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import re
import html


class PoToText:
    def _remove_sphinx(self, text):
        x = re.search(r"(:[^:]*:`([^`]*)`)", text)
        if x is None:
            return text

        out = text.replace(x.group(0), x.group(2))
        return self._remove_sphinx(out)

    def _write_str_to_text_file(self, text_file, text):
        if "@@image" in text:  # GNOME documentation images
            return

        if "external ref" in text:  # Gnome external images
            return

        if "image::" in text:  # Shpinx images
            return

        text = re.sub(r"[\t]", " ", text)
        text = re.sub(r"<br>|<br\/>", " ", text)
        text = html.unescape(text)
        text = re.sub(r"[_&~]", "", text)
        text = re.sub(r"<[^>]*>", "", text)  # Remove HTML tags

        text = self._remove_sphinx(text)
        text += "\n\n"

        text_file.write(text)

    def write_text_file(self, po_file, po_transonly, text_file):
        try:
            input_po = polib.pofile(po_file)
        except Exception as e:
            print("Unable to open PO file {0}: {1}".format(po_file, str(e)))
            return False

        text_file = open(text_file, "w")
        for entry in input_po.translated_entries():
            text = entry.msgstr

            if text is None or len(text) == 0:
                if entry.msgstr_plural is not None and len(entry.msgstr_plural) > 0:
                    text = entry.msgstr_plural[0]

            self._write_str_to_text_file(text_file, text)

            if entry.msgstr is None or len(entry.msgstr) == 0:
                if entry.msgstr_plural is not None and len(entry.msgstr_plural) > 1:
                    text = entry.msgstr_plural[1]
                    self._write_str_to_text_file(text_file, text)

        input_po.save(po_transonly)
        text_file.close()
        return True
