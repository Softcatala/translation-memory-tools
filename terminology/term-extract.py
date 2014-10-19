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

import logging
import os
import resource
import time
from collections import OrderedDict
from optparse import OptionParser

from corpus import Corpus
from devglossaryserializer import DevGlossarySerializer
from glossary import Glossary
from glossaryentry import GlossaryEntry
from metrics import Metrics
from referencesources import ReferenceSources
from translations import Translations
from userglossaryserializer import UserGlossarySerializer


src_directory = None
glossary_description = ''
glossary_file = None


def process_projects():

    global glossary_file, glossary_description

    corpus = Corpus(src_directory)
    corpus.process()

    reference_sources = ReferenceSources()
    reference_sources.read_sources()

    metrics = Metrics()
    metrics.create(corpus)

    # Select terms
    MAX_TERMS = 1000
    sorted_terms_by_tfxdf = sorted(metrics.tfxdf, key=metrics.tfxdf.get, reverse=True)

    # Developer report
    glossary_entries = OrderedDict()
    translations = Translations()
    selected_terms = sorted_terms_by_tfxdf[:MAX_TERMS] # Sorted by frequency

    for term in selected_terms:
        glossary_entries[term] = translations.create_for_word_sorted_by_frequency(corpus.documents, term, reference_sources)
    dev_glossary_serializer = DevGlossarySerializer()
    dev_glossary_serializer.create(u"dev-" + glossary_file + ".html", glossary_description, corpus,
                                   glossary_entries, reference_sources)

    # User report
    glossary_entries = []
    selected_terms = sorted(sorted_terms_by_tfxdf[:MAX_TERMS])  # Sorted by term

    glossary = Glossary()
    glossary.description = glossary_description
    for term in selected_terms:
        glossary_entry = GlossaryEntry()
        glossary_entry.source_term = term
        glossary_entry.translations = translations.create_for_word_sorted_by_frequency(corpus.documents, term, reference_sources)
        glossary.entries.append(glossary_entry)

    user_glossary_serializer = UserGlossarySerializer()
    user_glossary_serializer.create(glossary_file, glossary.get_dict(),
                                    reference_sources)


def read_parameters():

    global src_directory
    global glossary_description
    global glossary_file

    parser = OptionParser()

    parser.add_option("-s", "--srcdir",
                      action="store", type="string", dest="src_directory",
                      default="sc-tm-pos/",
                      help="Directory to find the PO files")

    parser.add_option("-c", "--comment",
                      action="store", type="string", dest="glossary_description",
                      default="",
                      help="HTML comment to add")

    parser.add_option("-t", "--html-file",
                      action="store", type="string", dest="glossary_file",
                      default="glossary",
                      help="Glossary file name to export")

    (options, args) = parser.parse_args()
    src_directory = options.src_directory
    glossary_description = options.glossary_description
    glossary_file = options.glossary_file

def init_logging():
    logfile = 'term-extract.log'

    if os.path.isfile(logfile):
        os.remove(logfile)

    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    logger = logging.getLogger('')


def using():
    usage=resource.getrusage(resource.RUSAGE_SELF)
    return '''usertime=%s systime=%s mem=%s mb
           '''%(usage[0],usage[1],
                (usage[2]*resource.getpagesize())/1000000.0)


def main():
    
    print "Extracts terminology"
    print "Use --help for assistance"

    start_time = time.time()
    init_logging()
    read_parameters()
    process_projects()
    end_time = time.time() - start_time
    print "time used to create the glossaries: " + str(end_time)
    print using()


if __name__ == "__main__":
    main()

