#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2013 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import logging
import os
import resource
import time
import json
import pystache
from collections import OrderedDict
from optparse import OptionParser
from terminology.corpus import Corpus
from terminology.devglossaryserializer import DevGlossarySerializer
from terminology.glossary import Glossary
from terminology.glossaryentry import GlossaryEntry
from terminology.metrics import Metrics
from terminology.referencesources import ReferenceSources
from terminology.translations import Translations


def process_template(template_file, filename, ctx):
    # Load template and process it.
    with open(template_file, "r") as template_fh:
        template = template_fh.read()

    parsed = pystache.Renderer()
    s = parsed.render(template, ctx)

    # Write output.
    with open(filename, "w") as output_fh:
        output_fh.write(s)


def generate_json(glossary, glossary_file):
    filename = glossary_file + ".json"
    all_entries = []
    for entry in glossary.entries:
        for translation in entry.translations:
            json_entry = {}
            json_entry["term"] = entry.source_term
            json_entry["translation"] = translation.translation
            json_entry["frequency"] = translation.frequency
            json_entry["percentage"] = translation.percentage
            json_entry["termcat"] = translation.termcat
            all_entries.append(json_entry)

    content = json.dumps(all_entries, indent=4)
    with open(filename, "w") as json_fh:
        json_fh.write(content)


def process_projects(src_directory, glossary_description, glossary_file):
    corpus = Corpus(src_directory)
    corpus.process()

    reference_sources = ReferenceSources()
    reference_sources.read_sources()

    metrics = Metrics()
    metrics.create(corpus)

    # Select terms
    MAX_TERMS = 8000
    sorted_terms_by_tfxdf = sorted(metrics.tfxdf, key=metrics.tfxdf.get, reverse=True)

    # Developer report
    glossary_entries = OrderedDict()
    translations = Translations()
    selected_terms = sorted_terms_by_tfxdf[:MAX_TERMS]  # Sorted by frequency

    for term in selected_terms:
        glossary_entries[term] = translations.create_for_word_sorted_by_frequency(
            corpus.documents, term, reference_sources
        )

    dev_glossary_serializer = DevGlossarySerializer()
    dev_glossary_serializer.create(
        "dev-" + glossary_file + ".html",
        glossary_description,
        corpus,
        glossary_entries,
        reference_sources,
    )

    # User report
    glossary_entries = []
    selected_terms = sorted(sorted_terms_by_tfxdf[:MAX_TERMS])  # Sorted by term

    glossary = Glossary(glossary_description)
    for term in selected_terms:
        glossary_entry = GlossaryEntry(
            term,
            translations.create_for_word_sorted_by_frequency(
                corpus.documents, term, reference_sources
            ),
        )
        glossary.entries.append(glossary_entry)

    glossary_entries = glossary.get_dict()
    process_template(
        "terminology/templates/userglossary-html.mustache",
        glossary_file + ".html",
        glossary_entries,
    )
    process_template(
        "terminology/templates/userglossary-csv.mustache",
        glossary_file + ".csv",
        glossary_entries,
    )

    generate_json(glossary, glossary_file)


def read_parameters():
    parser = OptionParser()
    parser.add_option(
        "-s",
        "--srcdir",
        action="store",
        type="string",
        dest="src_directory",
        default="terminology/sc-tm-pos/",
        help="Directory to find the PO files",
    )
    parser.add_option(
        "-c",
        "--comment",
        action="store",
        type="string",
        dest="glossary_description",
        default="",
        help="HTML comment to add",
    )
    parser.add_option(
        "-t",
        "--html-file",
        action="store",
        type="string",
        dest="glossary_file",
        default="glossary",
        help="Glossary file name to export",
    )

    (options, args) = parser.parse_args()

    return (options.src_directory, options.glossary_description, options.glossary_file)


def init_logging():
    logfile = "term_extract.log"

    if os.path.isfile(logfile):
        os.remove(logfile)

    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    logger = logging.getLogger("")


def main():
    print("Extracts terminology")
    print(
        "Extraction rule: appears in more than 1 document and has more than 4 occurrences"
    )
    print("Use --help for assistance")

    start_time = time.time()
    init_logging()
    src_directory, glossary_description, glossary_file = read_parameters()
    process_projects(src_directory, glossary_description, glossary_file)
    end_time = time.time() - start_time

    print("Time used to create the glossaries: " + str(end_time))
    usage = resource.getrusage(resource.RUSAGE_SELF)
    print(
        "usertime=%s systime=%s mem=%s mb"
        % (usage[0], usage[1], (usage[2] * resource.getpagesize()) / 1000000.0)
    )


if __name__ == "__main__":
    main()
