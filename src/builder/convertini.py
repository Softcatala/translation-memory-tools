# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Jordi Mas i Hernandez <jmas@softcatala.org>
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


class ConvertIni:
    def __init__(self, source_file, target_file, output_file):
        self.source_file = source_file
        self.target_file = target_file
        self.output_file = output_file

    def _parse_line(self, line):
        key = None
        value = None

        if "=" not in line:
            return key, value

        values = line.split("=", 1)
        if len(values) != 2:
            return key, value

        key = values[0]
        value = values[1]
        value = value.replace('"', "")
        return key.strip(), value.strip()

    def _read_source(self):
        lines = []
        strings = []
        with open(self.source_file) as f:
            lines = f.readlines()

        for line in lines:
            key, value = self._parse_line(line)
            if key is None:
                continue

            pair = (key.strip(), value.strip())
            strings.append(pair)

        return strings

    def _read_target(self):
        lines = []
        strings = {}
        with open(self.target_file) as f:
            lines = f.readlines()

        for line in lines:
            key, value = self._parse_line(line)
            if key is None:
                continue

            strings[key] = value

        return strings

    def convert(self):
        pofile = polib.POFile()

        pofile.metadata = {
            "Project-Id-Version": "1.0",
            "Report-Msgid-Bugs-To": "none",
            "POT-Creation-Date": "2007-10-18 14:00+0100",
            "PO-Revision-Date": "2007-10-18 14:00+0100",
            "Last-Translator": "none@none.org",
            "Language-Team": "Catalan <info@none.org>",
            "MIME-Version": "1.0",
            "Content-Type": "text/plain; charset=utf-8",
            "Content-Transfer-Encoding": "8bit",
            "Plural-Forms": "nplurals=2; plural=n != 1;",
        }

        entries = 0
        sources = self._read_source()
        targets = self._read_target()
        saved = set()
        for key, source in sources:
            if key in targets:
                target = targets[key]
            else:
                target = ""

            if source in saved:
                continue

            if len(source) == 0:
                continue

            entry = polib.POEntry(msgid=source, msgstr=target, comment=key)
            pofile.append(entry)
            entries = entries + 1
            saved.add(source)

        pofile.save(self.output_file)
