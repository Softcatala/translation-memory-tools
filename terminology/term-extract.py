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

import sys
sys.path.append('../src/')

import time
import math
import polib
import datetime
import cgi
import os
import logging
from optparse import OptionParser
from corpus import Corpus
from referencesources import ReferenceSources
from devglossaryserializer import DevGlossarySerializer

src_directory = None
html_comment = ''
hmtl_file = None


def process_projects():

    global html_file, html_comment

    corpus = Corpus(src_directory)
    corpus.process()

    # 
    # Processed
    #  
    #  1. term -> tf, idf, tfxidf

    # TF
    # Count the number of times each term occurs in each document and sum them all together; 
    # the number of times a term occurs in a document is called its term frequency.
    tf = {} # keyword -> frequency

    # IDF
    # It is obtained by dividing the total number of documents by the number of documents containing the term,
    idf = {}

    # TFxIDF
    # It is obtained by dividing the total number of documents by the number of documents containing the term,
    tfxidf = {}

    tfxdf = {}
    df = {}

    for source_word in corpus.source_words:
        frequency = 0
        documents_appear = 0
        for document_key_filename in corpus.documents.keys():
            if source_word in corpus.documents[document_key_filename]: # Word not in the file
                documents_appear += 1
                terms = corpus.documents[document_key_filename][source_word]
                frequency += len(terms)

        tf[source_word] = frequency
        _idf = math.log(len(corpus.documents) / documents_appear)
        idf[source_word] = _idf
        df[source_word] = documents_appear
        tfxidf[source_word] = frequency * _idf
        tfxdf[source_word] = frequency * documents_appear
        #print 'Source word {0} - {1} - {2}'.format(source_word.encode('utf-8'), frequency, _idf)

    reference_sources = ReferenceSources()
    reference_sources.read_sources()
    
    dev_glossary_serializer = DevGlossarySerializer()
    dev_glossary_serializer.create(html_file, html_comment, corpus, tfxdf, reference_sources)

    # tf x idf
    f = open('td-idx.txt','w')        
    terms = sorted(tfxidf, key=tfxidf.get,reverse=True)

    for term in terms:
        f.write('{0} - {1} (tf: {2}, idf: {3})\n'.format(term.encode('utf-8'), tfxidf[term],
               tf[term], idf[term]))
    f.close()
        
def read_parameters():

    global src_directory
    global html_comment
    global html_file
   
    parser = OptionParser()

    parser.add_option("-s", "--srcdir",
                      action="store", type="string", dest="src_directory",
                      #default = "/home/jordi/sc/other/src/pos/",
                      default = "sc-tm-pos/",
                      help="Directory to find the PO files")

    parser.add_option("-c", "--comment",
                      action="store", type="string", dest="html_comment",
                      default = "",
                      help="HTML comment to add")

    parser.add_option("-t", "--html-file",
                      action="store", type="string", dest="html_file",
                      default = "glossary.html",
                      help="HTML file to export")

    (options, args) = parser.parse_args()
    src_directory = options.src_directory
    html_comment = options.html_comment
    html_file = options.html_file

def init_logging():
    logfile = 'term-extract.log'

    if os.path.isfile(logfile):
        os.remove(logfile)

    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    logger = logging.getLogger('')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)

def main():
    
    print "Extracts terminology"
    print "Use --help for assistance"

    start_time = time.time()
    init_logging()
    read_parameters()
    process_projects()
    end_time = time.time() - start_time
    print "time used to create the glossaries: " + str(end_time)


if __name__ == "__main__":
    main()

