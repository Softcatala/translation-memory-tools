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


class Reference(object):
    def __init__(self, name, short_name):
        self.name = name
        self.short_name = short_name
        self.terms = {}  # key -> source term, value: list of translations


class ReferenceSources(object):
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

    def get_translations_for_term_in_reference(self, term, short_name):
        references = []

        for ref in self.references:
            if ref.short_name is short_name:
                reference = ref
                break

        if term in reference.terms.keys():
            return reference.terms[term]
        else:
            return []

    def get_terms_not_used_from_references(self, terms):
        not_used_references = []

        for reference in self.references:
            not_used_reference = Reference(reference.name, reference.short_name)
            not_used_references.append(not_used_reference)

            for term in reference.terms:
                if term not in terms:
                    # Terms should contain a translation but we do not need
                    # for this propose. Review data structures
                    not_used_reference.terms[term] = None

        return not_used_references

    def _read_source(self, name, short_name, filename):
        pofile = polib.pofile(filename)
        reference = Reference(unicode(name, "utf-8"), short_name)

        for entry in pofile:
            term = entry.msgid.lower()
            translation = entry.msgstr.lower()

            if term in reference.terms:
                translations = reference.terms[term]
            else:
                translations = []

            translations.append(translation)
            reference.terms[term] = translations

        self.references.append(reference)

    def read_sources(self):
        self._read_source('Recull de Softcatalà', 'r', 'recull/recull-glossary.po')
        self._read_source('Terminologia de Microsoft', 'm', 'microsoft/microsoft-terms.po')
        self._read_source('TERMCAT', 't', 'termcat/termcat.po')
