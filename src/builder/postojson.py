# -*- encoding: utf-8 -*-
#
# Copyright (c) 2023 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import json
import os
import polib
from builder.findfiles import FindFiles
from builder.jsonbackend import JsonBackend


class POsToJson(object):
    def __init__(self, po_directory, debug_keyword=None, projects_names=None):
        self.projects = 0
        self.options = []
        self.sentences_indexed = 0
        self.sentences = 0
        self.po_directory = po_directory
        self.debug_keyword = debug_keyword
        self.projects_names = projects_names
        self.index_fh = open("index_data.json", "w")
        self.index_fh.write("[\n")
        self.first_entry = True

    def process_projects(self):
        json = JsonBackend("../cfg/projects/")
        json.load()

        for project_dto in json.projects:
            if self.projects_names:
                found = False

                for project_name in self.projects_names:
                    project_dto_lower = project_dto.name.lower().strip()
                    if project_name.lower().strip() == project_dto_lower:
                        found = True

                if not found:
                    continue

            if project_dto.selectable:
                self.options.append(project_dto.name)

            self._process_project(
                project_dto.project_id,
                project_dto.name,
                project_dto.filename,
                project_dto.softcatala,
            )
            self.projects += 1

        print(
            "Total sentences considered {0}, sentences written {1}".format(
                self.sentences, self.sentences_indexed
            )
        )
        self.save_index()

    def _get_comment(self, entry):
        """
        PO files can contain 3 types of comments:

            # translators comments
            #. extracted
            #: location

        We import only translator's comments and extracted that we concatenate
        to make it transparent to the search
        """

        comment = entry.tcomment
        if entry.comment is not None:
            if entry.tcomment is None:
                comment = entry.comment
            else:
                comment += "\r\n" + entry.comment

        return comment

    def _process_project(self, project_id, project_name, filename, softcatala):
        entries = set()
        directory = os.path.join(self.po_directory, "individual_pos/", project_id)
        findFiles = FindFiles()
        for filename in findFiles.find_recursive(directory, "*.po"):
            self._process_file(project_id, project_name, filename, softcatala, entries)

    def _write_entry(self, entries, s, t, x, c, project_id, project_name, softcatala):
        if self.debug_keyword is not None and self.debug_keyword.strip() == s:
            print("Source: " + s)
            print("Translation: " + t)
            print("Context: " + str(x))
            print("Comment: " + str(c))

        if s is None or len(s) == 0 or t is None or len(t) == 0:
            return

        entry_text = s + t + str(x)
        if entry_text in entries:
            return

        entries.add(entry_text)

        self.sentences_indexed += 1
        self.write_entry(
            source=s,
            target=t,
            comment=c,
            context=x,
            project_name=project_name,
            project_id=project_id,
            softcatala=softcatala,
        )

    def _process_file(self, project_id, project_name, filename, softcatala, entries):
        try:
            input_po = polib.pofile(filename)

            for entry in input_po.translated_entries():
                self.sentences += 1
                s = entry.msgid
                t = entry.msgstr
                x = entry.msgctxt
                c = self._get_comment(entry)

                if t is None or len(t) == 0:
                    # msgstr_plural is a dictionary where the key is the index and
                    # the value is the localised string
                    if entry.msgstr_plural is not None and len(entry.msgstr_plural) > 0:
                        t = entry.msgstr_plural[0]

                self._write_entry(
                    entries, s, t, x, c, project_id, project_name, softcatala
                )

                if entry.msgstr is None or len(entry.msgstr) == 0:
                    if entry.msgstr_plural is not None and len(entry.msgstr_plural) > 1:
                        self.sentences += 1
                        s = entry.msgid_plural
                        t = entry.msgstr_plural[1]
                        self._write_entry(
                            entries, s, t, x, c, project_id, project_name, softcatala
                        )

        except Exception as detail:
            print("Exception: " + str(detail))

    def write_entry(
        self, source, target, comment, context, project_id, project_name, softcatala
    ):
        if self.first_entry:
            self.first_entry = False
        else:
            self.index_fh.write(",\n")

        d = {}
        d["s"] = source
        d["t"] = target
        d["c"] = comment
        d["x"] = context
        d["pi"] = project_id
        d["pn"] = project_name
        d["sc"] = softcatala

        json.dump(d, self.index_fh, indent=4)

    def save_index(self):
        self.index_fh.write("]\n")
        self.index_fh.close()
