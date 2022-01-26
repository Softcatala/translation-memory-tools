# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import tempfile
import unittest

import polib
from whoosh.writing import *

from web.indexcreator import IndexCreator


class IndexWriterMock (IndexWriter):

    def __init__(self):
        self.store = []

    def add_document(self, **fields):
        d = dict()
        d.update(fields)
        self.store.append(d)


class TestIndexCreator(unittest.TestCase):

    minipo = r"""#
msgid ""
msgstr ""
"Project-Id-Version: program 2.1-branch\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2006-01-09 07:15+0100\n"
"PO-Revision-Date: 2004-03-30 17:02+0200\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

# Please remember to do something
#: ../dir/file.xml.in.h:1 ../dir/file2.xml.in.h:4
msgctxt "Context"
msgid "Power off the selected virtual machines"
msgstr "Apaga les màquines virtuals seleccionades"
"""

    minipo_plural = r"""#
msgid ""
msgstr ""
"Project-Id-Version: program 2.1-branch\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2006-01-09 07:15+0100\n"
"PO-Revision-Date: 2004-03-30 17:02+0200\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

# Please remember to do something
#: ../dir/file.xml.in.h:1 ../dir/file2.xml.in.h:4
msgctxt "Context"
msgid "Delete this photo from camera?"
msgid_plural "Delete these %d photos from camera?"
msgstr[0] "Voleu suprimir aquesta fotografia de la càmera?"
msgstr[1] "Voleu suprimir aquestes %d fotografies de la càmera?"
"""

    def _dump_po_to_file(self, filename):
        tmpfile = tempfile.NamedTemporaryFile()
        f = open(tmpfile.name, 'w')
        f.write(filename)
        return tmpfile

    def test_process_project(self):

        tmpfile = self._dump_po_to_file(self.minipo)

        index = IndexCreator('.')
        index.writer = IndexWriterMock()
        index._process_file('test_project', tmpfile.name, False, set())
        stored = index.writer.store

        self.assertEquals(stored[0]['source'], u'Power off the selected virtual machines')
        self.assertEquals(stored[0]['target'], u'Apaga les màquines virtuals seleccionades')
        self.assertEquals(stored[0]['context'], 'Context')
        self.assertEquals(stored[0]['comment'], 'Please remember to do something\r\n')
        self.assertEquals(stored[0]['softcatala'], False)
        self.assertEquals(stored[0]['project'], 'test_project')
        self.assertEquals(index.words, 5)
        self.assertEquals(index.sentences, 1)
        self.assertEquals(index.sentences_indexed, 1)

    def test_process_project_plural(self):

        tmpfile = self._dump_po_to_file(self.minipo_plural)

        index = IndexCreator('.')
        index.writer = IndexWriterMock()
        index._process_file('test_project', tmpfile.name, False, set())
        stored = index.writer.store
        self.assertEquals(stored[0]['source'], u'Delete this photo from camera?')
        self.assertEquals(stored[0]['target'], u'Voleu suprimir aquesta fotografia de la càmera?')

        self.assertEquals(stored[1]['source'], u'Delete these %d photos from camera?')
        self.assertEquals(stored[1]['target'], u'Voleu suprimir aquestes %d fotografies de la càmera?')

        self.assertEquals(index.sentences, 2)
        self.assertEquals(index.sentences_indexed, 2)


    def test_get_comment_both(self):
        index = IndexCreator('.')
        entry = polib.POEntry()
        entry.comment = 'comment'
        entry.tcomment = 'tcomment'
        comment = index._get_comment(entry)
        self.assertEquals(comment, 'tcomment\r\ncomment')


if __name__ == '__main__':
    unittest.main()
