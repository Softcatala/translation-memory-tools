#!/usr/bin/env python
# -*- encoding: utf-8 -*-
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

import polib

class Reference:
    def __init__(self, name, short_name):
        self.name = unicode(name, "utf-8")
        self.short_name = short_name
        self.terms = {}

class ReferenceSources:
    '''Loads different PO files that we use as reference sources'''
    '''like TERMCAT or Microsoft glossaries'''
   
    def __init__(self):
        self.stop_words = set()
        self.references = []

    def get_references_for_term_in(self, term):
        references = []
        for reference in self.references:
            if term in reference.terms.keys():
                references.append(reference)

        return references
        
    def _read_source(self, name, short_name, filename):

        pofile = polib.pofile(filename)
            
        reference = Reference(name, short_name)

        for entry in pofile:
            reference.terms[entry.msgid.lower()] = entry.msgstr.lower()

        self.references.append(reference)

    def read_sources(self):
        self._read_source('Recull de Softcatalà', 'r', 'recull/recull-glossary.po')
        self._read_source('Terminologia de Microsoft', 'm', 'microsoft/microsoft-terms.po')
        self._read_source('TERMCAT', 't', 'termcat/termcat.po')

