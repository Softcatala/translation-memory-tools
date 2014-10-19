#!/usr/bin/env python
# -*- encoding: utf-8 -*-
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


class GlossaryEntry:
    '''Represents an entry to be written in a glossary'''

    def __init__(self):
        self.source_term = u''
        self.translations = []
        self.percentage = 0  # Percentage of frequency across all options

    def get_dict(self):
        d = {}
        d[u'source'] = self.source_term
        d[u'translation'] = self.translations[0].translation
        translations = []

        for translation in self.translations:
            translations.append(translation.get_dict())

        d[u'translations'] = translations
        return d
