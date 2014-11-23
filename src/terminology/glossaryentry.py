#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2014 Jordi Mas i Hernandez <jmas@softcatala.org>
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


class GlossaryEntry(object):
    """Represents an entry to be written in a glossary."""

    def __init__(self, source_term=u'', translations=None):
        self.source_term = source_term
        self.translations = translations is None and [] or translations
        self.percentage = 0  # Percentage of frequency across all options.

    def get_dict(self):
        translations = []

        for translation in self.translations:
            translations.append(translation.get_dict())

        return {
            u'source': self.source_term,
            u'translation': self.translations[0].translation,
            u'translations': translations,
        }
