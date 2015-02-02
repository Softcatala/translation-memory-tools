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


class Translation(object):
    def __init__(self):
        self.translation = u''
        self.frequency = 0
        self.percentage = 0  # Percentage of frequency across all options
        self.references_short_name = []  # A list of references

    @property
    def termcat(self):
        return len(self.references_short_name) > 0

    def get_dict(self):
        d = {
            u'translation': self.translation,
            u'frequency': self.frequency,
            u'percentage': self.percentage,
        }

        if self.termcat:
            d[u'termcat'] = True

        return d


class Translations(object):
    '''From a list of unsorted translations creates the final translations'''
    '''for the glossary, grouping same translation units and sorting them by'''
    '''frequency'''

    def _add_reference_translations(self, term, reference_sources,
                                    translations):

        # Translations from references (TERMCAT only for now)
        reference_translations = reference_sources.get_translations_for_term_in_reference(term, 't')

        if len(reference_translations) == 0:
            return translations

        translations_with_references = list(translations)

        for reference_translation in reference_translations:
            found = False
            for idx in range(0, len(translations)):
                if translations[idx].translation == reference_translation:
                    translation_obj_item = translations[idx]
                    translation_obj_item.references_short_name.append('t')
                    translations_with_references[idx] = translation_obj_item
                    found = True
                    break

            if not found:
                translation_obj_item = Translation()
                translation_obj_item.translation = reference_translation
                translation_obj_item.frequency = 0
                translation_obj_item.references_short_name.append('t')
                translations_with_references.append(translation_obj_item)

        return translations_with_references

    def create_for_word_sorted_by_frequency(self, documents, term,
                                            reference_sources):
        translations = {} # key: english keyword -> value: list of translation objects
        for document_key_filename in documents.keys():
            if term not in documents[document_key_filename]:
                continue

            for translated in documents[document_key_filename][term]:
                #print "     t:" +m translated.encode('utf-8')
                if term in translations:
                    translation_list = translations[term]
                else:
                    translation_list = []

                found = False
                # Consolidate repeated translations
                for i in range(0, len(translation_list)):
                    if translation_list[i].translation == translated:
                        translation_obj_item = translation_list[i]
                        translation_obj_item.frequency += 1
                        translation_list[i] = translation_obj_item
                        found = True
                        break

                # It is a new translation
                if not found:
                    translation_obj_item = Translation()
                    translation_obj_item.translation = translated
                    translation_obj_item.frequency = 1
                    translation_list.append(translation_obj_item)

                translations[term] = translation_list

        translations[term] = self._add_reference_translations(term, reference_sources, translations[term])

        # Calculate frequencies and percentages
        for translation_obj_list in translations.values():

            translation_obj_list_sorted = sorted(translation_obj_list, key=lambda x: x.frequency, reverse=True)

            all_frequencies = 0

            for translation in translation_obj_list_sorted:
                all_frequencies += translation.frequency

            for translation in translation_obj_list_sorted:
                translation.percentage = translation.frequency * 100 / all_frequencies

        return translation_obj_list_sorted
