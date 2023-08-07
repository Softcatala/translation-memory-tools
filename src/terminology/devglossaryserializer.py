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

import cgi
import datetime
import sys
import time

import polib

from .corpus import Corpus
from .referencesources import ReferenceSources
from html import escape as html_escape


class ReferenceMatches(object):
    def __init__(self):
        self.first_50 = 0
        self.first_100 = 0
        self.first_500 = 0
        self.first_2000 = 0


class DevGlossarySerializer:
    def create_text_dump(self, glossary_entries):
        f = open("glossary.txt", "w")

        for term in glossary_entries:
            translations = glossary_entries[term]
            f.write(
                "{0};{1}\n".format(
                    term.encode("utf-8"), translations[0].translation.encode("utf-8")
                )
            )

        f.close()

    def create(
        self, html_file, html_comment, corpus, glossary_entries, reference_sources
    ):
        item = 0
        words_cnt = [0, 0, 0]

        reference_matches = {}
        for reference in reference_sources.references:
            reference_matches[reference.name] = ReferenceMatches()

        f = open(html_file, "w")

        html = (
            "<!DOCTYPE html>"
            "<html>"
            "<head>"
            '<meta http-equiv="content-type" content="text/html; charset=UTF-8" />'
            "</head>"
            "<body>"
            "<p><b>Comentaris</b></p>"
            "<ul>"
            "<li>Glossari generat computacionalment al final del mateix hi ha dades sobre la generació.</li>"
            "<li>La columna opcions considerades indica quines altres traduccions apareixen per aquest terme i s'han considerat.</li>"
            "<li>La columna català és l'opció més comuna.</li>"
            "<li>Usada indica el % d'ús respecte a altres opcions i coincidències els cops que s'ha trobat.</li>"
            "<li>(r) indica el terme es troba a l'últim Recull de termes publicat.</li>"
            "<li>(m) indica el terme es troba a la terminologia de Microsoft.</li>"
            "<li>(t) indica el terme es troba a la terminologia del TERMCAT.</li>"
            "</ul>"
            '<table border="1" cellpadding="5px" cellspacing="5px" style="border-collapse:collapse;">'
            "<tr>"
            "<th>#</th>"
            "<th>Anglès</th>"
            "<th>Català</th>"
            "<th>Opcions considerades</th>"
            "</tr>"
        )
        f.write(html)

        for term in glossary_entries:
            sources = " "

            word_len = len(term.split(" "))
            if word_len <= 3:
                words_cnt[word_len - 1] += 1

            for reference in reference_sources.get_references_for_term_in(term):
                if reference is not None:
                    sources += "({0})".format(reference.short_name)

                    if item < 50:
                        reference_matches[reference.name].first_50 += 1

                    if item < 100:
                        reference_matches[reference.name].first_100 += 1

                    if item < 500:
                        reference_matches[reference.name].first_500 += 1

                    if item < 2000:
                        reference_matches[reference.name].first_2000 += 1

            item += 1

            options = ""
            translations = glossary_entries[term]
            for translation in translations:
                opt = "<p>- {0} (usada {1:1.2f}%, coincidències {2})</p>"
                options += opt.format(
                    html_escape(translation.translation),
                    translation.percentage,
                    translation.frequency,
                )

            html = (
                "<tr>"
                "<td>{0}</td>"
                "<td>{1}{2}</td>"
                "<td>{3}</td>"
                "<td>{4}</td>"
                "</tr>"
            ).format(
                item,
                html_escape(term),
                sources,
                html_escape(translations[0].translation),
                options,
            )
            f.write(html)

        html = "</table>"

        not_used = reference_sources.get_terms_not_used_from_references(
            corpus.source_words
        )
        for reference in not_used:
            html += (
                "<p><b>Termes no usats de la font {0}</b></p>"
                '<table border="1" cellpadding="5px" cellspacing="5px" style="border-collapse:collapse;">'
                "<tr>"
                "<th>Terme</th>"
                "</tr>"
            ).format(reference.name)

            for term in sorted(reference.terms.keys()):
                html += ("<tr>" "<td>{0}</td>" "</tr>").format(html_escape(term))

            html += "</table>"

        f.write(html)

        percentage = 0
        if corpus.strings > 0:
            percentage = 100 * corpus.strings_selected / corpus.strings

        html = (
            "<p>Data de generació: {0}</p>"
            "<p>Cadenes analitzades: {1}</p>"
            "<p>Cadenes seleccionades: {2} - {3}%</p>"
            "<p>Termes únics totals selecionats: {4}</p>"
            "<p><b>Mesures de qualitat</b></p>"
        )
        html = html.format(
            datetime.date.today().strftime("%d/%m/%Y"),
            corpus.strings,
            corpus.strings_selected,
            percentage,
            len(corpus.source_words),
        )

        for name in reference_matches.keys():
            match = reference_matches[name]
            temp = (
                "<p>Dels 50 primers termes quants eren al {0}: {1}% ({2})</p>"
                "<p>Dels 100 primers termes quants eren al {3}: {4}% ({5})</p>"
                "<p>Dels 500 primers termes quants eren al {6}: {7}% ({8})</p>"
                "<p>Dels 2000 primers termes quants eren al {9}: {10}% ({11})</p>"
            )
            html += temp.format(
                name,
                match.first_50 * 100 / 50,
                match.first_50,
                name,
                match.first_100 * 100 / 100,
                match.first_100,
                name,
                match.first_500 * 100 / 500,
                match.first_500,
                name,
                match.first_2000 * 100 / 2000,
                match.first_2000,
            )

        temp = (
            "<p>{0} cadenes amb 1 paraula, {1} cadenes amb 2 paraules, "
            "{2} cadenes amb 3 paraules</p>"
        )
        html += temp.format(words_cnt[0], words_cnt[1], words_cnt[2])

        if len(html_comment) > 0:
            comment = html_comment
            html += "Comentari de generació: {0}".format(comment)

        html += "</body>" "</html>"
        f.write(html)
        f.close()

        self.create_text_dump(glossary_entries)
