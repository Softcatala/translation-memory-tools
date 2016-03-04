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


class ReferenceMatches(object):

    def __init__(self):
        self.first_50 = 0
        self.first_100 = 0
        self.first_500 = 0
        self.first_2000 = 0


class DevGlossarySerializer():

    def create_text_dump(self, glossary_entries):
        f = open('glossary.txt', 'w')

        for term in glossary_entries:
            translations = glossary_entries[term]
            f.write('{0};{1}\n'.format(term.encode('utf-8'),
                    translations[0].translation.encode('utf-8')))

        f.close()

    def create(self, html_file, html_comment, corpus, glossary_entries,
               reference_sources):
        item = 0
        words_cnt = [0, 0, 0]

        reference_matches = {}
        for reference in reference_sources.references:
            reference_matches[reference.name] = ReferenceMatches()

        f = open(html_file, 'w')

        html = (u'<!DOCTYPE html>'
                u'<html>'
                u'<head>'
                u'<meta http-equiv="content-type" content="text/html; charset=UTF-8" />'
                u'</head>'
                u'<body>'
                u'<p><b>Comentaris</b></p>'
                u'<ul>'
                u'<li>Glossari generat computacionalment al final del mateix hi ha dades sobre la generació.</li>'
                u"<li>La columna opcions considerades indica quines altres traduccions apareixen per aquest terme i s'han considerat.</li>"
                u"<li>La columna català és l'opció més comuna.</li>"
                u"<li>Usada indica el % d'ús respecte a altres opcions i coincidències els cops que s'ha trobat.</li>"
                u"<li>(r) indica el terme es troba a l'últim Recull de termes publicat.</li>"
                u'<li>(m) indica el terme es troba a la terminologia de Microsoft.</li>'
                u'<li>(t) indica el terme es troba a la terminologia del TERMCAT.</li>'
                u'</ul>'
                u'<table border="1" cellpadding="5px" cellspacing="5px" style="border-collapse:collapse;">'
                u'<tr>'
                u'<th>#</th>'
                u'<th>Anglès</th>'
                u'<th>Català</th>'
                u'<th>Opcions considerades</th>'
                u'</tr>')
        f.write(html)

        for term in glossary_entries:
            sources = ' '

            word_len = len(term.split(' '))
            if word_len <= 3:
                words_cnt[word_len - 1] += 1

            for reference in reference_sources.get_references_for_term_in(term):
                if reference is not None:
                    sources += '({0})'.format(reference.short_name)

                    if item < 50:
                        reference_matches[reference.name].first_50 += 1

                    if item < 100:
                        reference_matches[reference.name].first_100 += 1

                    if item < 500:
                        reference_matches[reference.name].first_500 += 1

                    if item < 2000:
                        reference_matches[reference.name].first_2000 += 1

            item += 1

            options = ''
            translations = glossary_entries[term]
            for translation in translations:
                opt = u'<p>- {0} (usada {1}%, coincidències {2})</p>'
                options += opt.format(cgi.escape(translation.translation),
                                      translation.percentage,
                                      translation.frequency)

            html = (u'<tr>'
                    u'<td>{0}</td>'
                    u'<td>{1}{2}</td>'
                    u'<td>{3}</td>'
                    u'<td>{4}</td>'
                    u'</tr>').format(item, cgi.escape(term), sources,
                                     cgi.escape(translations[0].translation),
                                     options)
            f.write(html)

        html = u'</table>'

        not_used = reference_sources.get_terms_not_used_from_references(corpus.source_words)
        for reference in not_used:
            html += (u'<p><b>Termes no usats de la font {0}</b></p>'
                     u'<table border="1" cellpadding="5px" cellspacing="5px" style="border-collapse:collapse;">'
                     u'<tr>'
                     u'<th>Terme</th>'
                     u'</tr>').format(reference.name)

            for term in sorted(reference.terms.keys()):
                html += (u'<tr>'
                         u'<td>{0}</td>'
                         u'</tr>').format(cgi.escape(term))

            html += u'</table>'

        f.write(html)

        percentage = 0
        if corpus.strings > 0:
            percentage = 100 * corpus.strings_selected / corpus.strings

        html = (u'<p>Data de generació: {0}</p>'
                u'<p>Cadenes analitzades: {1}</p>'
                u'<p>Cadenes seleccionades: {2} - {3}%</p>'
                u'<p>Termes únics totals selecionats: {4}</p>'
                u'<p><b>Mesures de qualitat</b></p>')
        html = html.format(datetime.date.today().strftime("%d/%m/%Y"),
                           corpus.strings, corpus.strings_selected, percentage,
                           len(corpus.source_words))

        for name in reference_matches.keys():
            match = reference_matches[name]
            temp = (u'<p>Dels 50 primers termes quants eren al {0}: {1}% ({2})</p>'
                    u'<p>Dels 100 primers termes quants eren al {3}: {4}% ({5})</p>'
                    u'<p>Dels 500 primers termes quants eren al {6}: {7}% ({8})</p>'
                    u'<p>Dels 2000 primers termes quants eren al {9}: {10}% ({11})</p>')
            html += temp.format(name, match.first_50 * 100 / 50, match.first_50,
                                name, match.first_100 * 100 / 100,
                                match.first_100, name,
                                match.first_500 * 100 / 500, match.first_500,
                                name, match.first_2000 * 100 / 2000,
                                match.first_2000)

        temp = (u'<p>{0} cadenes amb 1 paraula, {1} cadenes amb 2 paraules, '
                u'{2} cadenes amb 3 paraules</p>')
        html += temp.format(words_cnt[0], words_cnt[1], words_cnt[2])

        if len(html_comment) > 0:
            comment = html_comment
            html += u"Comentari de generació: {0}".format(comment)

        html += (u'</body>'
                 u'</html>')
        f.write(html)
        f.close()

        self.create_text_dump(glossary_entries)
