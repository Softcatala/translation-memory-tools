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

from findfiles import FindFiles

class Corpus:
    '''Loads different PO files that build the corpus'''
    '''Strings that are not suitable candidates are discared'''
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

    def _read_stop_words(self):

        _file = open("stop-words.txt")

        while True:
            line = _file.readline()
            if not line:
                break

            word = line.strip()
            word = word.lower()
            self.stop_words.add(word)

    def _clean_string(self, result):

        chars = {'_', '&', '~',  # Accelarators
                ':', ',', '...', u'…'  # Punctuations
              }

        for c in chars:
            result = result.replace(c, '')

        #remove all the leading and trailing whitespace characters 
        result = result.strip()
        result = result.lower()
        return result


    def _should_select_string(self, source):

        # Only 1 word terms for now
        if len(source.split()) > 1:
            return False

        # Single words without spaces that are very long
        if len(source) > 30:
            return False
    
        # Single chars provide no value
        if len(source) < 2:
            return False

        # Numeric only strings should not be considered
        if source.isdigit():
            return False

        if source in self.stop_words:
            return False

        return True

    #
    # Output: Dictionary key: document, terms dictionary:
    #          Terms dictionary -> key: source term (delete), value:list <trgs> (suprimeix, esborra)
    #
    def process(self):

        self._read_stop_words()

        findFiles = FindFiles()

        f = open('corpus.txt', 'w')

        for filename in findFiles.find(self.directory, '*.po'):
            print "Reading: " + filename

            pofile = polib.pofile(filename)

            terms = {}
            for entry in pofile.translated_entries():

                self.strings = self.strings + 1

                msgid = self._clean_string(entry.msgid)
                if self._should_select_string(msgid) is False:
                    continue
    
                self.strings_selected = self.strings_selected + 1
                msgstr = self._clean_string(entry.msgstr)

                log = u'source:{0} ({1}) - target:{2} ({3}) - {4}\n'.format(msgid, entry.msgid, \
                        msgstr, entry.msgstr, filename)

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
        #self.dump_documents()

    def dump_documents(self):

        for document_key_filename in self.documents.keys():
            print document_key_filename
            for terms in self.documents[document_key_filename].keys():
                print "  s({0}):{1}".format(len(self.documents[document_key_filename][terms]), terms.encode('utf-8'))
                for translation in self.documents[document_key_filename][terms]:
                    print "     t:" + translation.encode('utf-8')

