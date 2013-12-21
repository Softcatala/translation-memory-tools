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

class Translation:
    def __init__(self):
        self.translation = ''
        self.frequency = 0
        self.percentage = 0  # Percentage of frequency across all options

class Serializer:

    def create_translations_for_word_sorted_by_frequency(self, documents, term):

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
                for i in range(0, len(translation_list)):
                    if translation_list[i].translation == translated:
                        translation_obj_item = translation_list[i]
                        translation_obj_item.frequency += 1
                        translation_list[i] = translation_obj_item
                        found = True
                        break

                if found is False:
                    translation_obj_item = Translation()
                    translation_obj_item.translation = translated
                    translation_obj_item.frequency = 1
                    translation_list.append(translation_obj_item)

                translations[term] = translation_list

        for translation_obj_list in translations.values():

            translation_obj_list_sorted = sorted(translation_obj_list, key=lambda x: x.frequency, reverse=True)

            all_frequencies = 0

            for translation in translation_obj_list_sorted:
                all_frequencies += translation.frequency

            for translation in translation_obj_list_sorted:
                translation.percentage = translation.frequency * 100 / all_frequencies

        return translation_obj_list_sorted
