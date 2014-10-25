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

import math


class Metrics(object):

    def __init__(self):
        # All the dictionaries are word -> metric
        # TODO: Consider a word pointing to a class with all the metrics for the word

        # TF
        # Count the number of times each term occurs in each document and sum them all together;
        # the number of times a term occurs in a document is called its term frequency.
        self.tf = {}

        # IDF
        # It is obtained by dividing the total number of documents by the number of documents containing the term,
        self.idf = {}

        # TFxIDF
        self.tfxidf = {}

        self.tfxdf = {}

        # Document frequency
        self.df = {}

    def create(self, corpus):
        for source_word in corpus.source_words:
            frequency = 0
            documents_appear = 0
            for document_key_filename in corpus.documents.keys():
                if source_word in corpus.documents[document_key_filename]:  # Word is the file
                    documents_appear += 1
                    terms = corpus.documents[document_key_filename][source_word]
                    frequency += len(terms)

            self.tf[source_word] = frequency
            idf = math.log(len(corpus.documents) / documents_appear)
            self.idf[source_word] = idf
            self.df[source_word] = documents_appear
            self.tfxidf[source_word] = frequency * idf
            self.tfxdf[source_word] = frequency * documents_appear
