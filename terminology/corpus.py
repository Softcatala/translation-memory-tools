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
import logging

from findfiles import FindFiles


class Corpus:
    '''Loads different PO files that build the corpus'''
    '''Strings that are not suitable candidates are discarded'''
    '''We do a minimum clean up of strings'''

    def __init__(self, directory):
        self.directory = directory
        self.source_words = set()
        self.documents = {}
        self.files = 0
        self.strings = 0
        self.strings_selected = 0
        self.translations = 0
        self.stop_words = set()

    def _read_stop_words(self, stopwords_file):
        while True:
            line = stopwords_file.readline()
            if not line:
                break
            word = line.strip()
            word = word.lower()
            self.stop_words.add(word)

    def _clean_string(self, result):
        chars = {'_', '&', '~',  # Accelerators
                 ':', ',', '...', u'…'  # Punctuations
        }
        for c in chars:
            result = result.replace(c, '')

        #remove all the leading and trailing whitespace characters
        result = result.strip()
        result = result.lower()
        return result

    def _should_select_string(self, source, target):
        words = len(source.split())

        # Only up to 3 words terms for now
        if words > 3:
            return False

        # Single words without spaces that are very long
        if words == 1 and len(source) > 30:
            msg = "Discard: long word '{0}'".format(source.encode('utf-8'))
            logging.info(msg)
            return False

        # Single chars provide no value
        if len(source) < 2:
            msg = "Discard: single chart '{0}'".format(source.encode('utf-8'))
            logging.info(msg)
            return False

        # Numeric only strings should not be considered
        if source.isdigit():
            msg = "Discard: is digit '{0}'".format(source.encode('utf-8'))
            logging.info(msg)
            return False

        if source in self.stop_words:
            msg = "Discard: stop word '{0}'".format(source.encode('utf-8'))
            logging.info(msg)
            return False

        # We are ignoring strings with html tags or string formatters
        # This also affects strings like <shift>f10
        chars = {'<', '>', '%', '{', '}'}
        for c in chars:
            if c in source:
                msg = "Discard: invalid chars '{0}'".format(source.encode('utf-8'))
                logging.info(msg)
                return False

        if len(target) == 0:
            return False
        return True


    #
    # Output: Dictionary key: document, terms dictionary:
    #          Terms dictionary -> key: source term (delete), value:list <trgs> (suprimeix, esborra)
    #
    def process(self):
        stopwords_file = open("stop-words/stop-words.txt")
        self._read_stop_words(stopwords_file)

        findFiles = FindFiles()

        f = open('corpus.txt', 'w')

        for filename in findFiles.find(self.directory, '*.po'):
            print("Reading: " + filename)

            pofile = polib.pofile(filename)

            terms = {}
            for entry in pofile.translated_entries():

                self.strings += 1

                msgid = self._clean_string(entry.msgid)
                msgstr = self._clean_string(entry.msgstr)

                if self._should_select_string(msgid, msgstr) is False:
                    continue

                self.strings_selected += 1

                log = u'source:{0} ({1}) - target:{2} ({3}) - {4}\n'. \
                      format(msgid, entry.msgid, msgstr, entry.msgstr, filename)

                f.write(log.encode('utf-8'))

                if not msgid in terms.keys():
                    translations = []
                else:
                    translations = terms[msgid]

                self.source_words.add(msgid)
                translations.append(msgstr)
                terms[msgid] = translations

            self.documents[filename] = terms
            self.files += 1
            #if self.files > 3:
            #    break

        f.close()
        #self.dump_documents

    def dump_documents(self):
        '''For debugging proposes'''
        for document_key_filename in self.documents.keys():
            print document_key_filename
            for terms in self.documents[document_key_filename].keys():
                print "  s({0}):{1}".format(len(self.documents[document_key_filename][terms]), terms.encode('utf-8'))
                for translation in self.documents[document_key_filename][terms]:
                    print "     t:" + translation.encode('utf-8')
