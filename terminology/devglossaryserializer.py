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


class ReferenceMatches:

    def __init__(self):
        self.first_50 = 0
        self.first_100 = 0
        self.first_500 = 0
        self.first_2000 = 0


class DevGlossarySerializer():

    def create_text_dump(self, documents, glossary_entries, reference_sources):
        f = open('glossary.txt', 'w')

        for term in glossary_entries:
            translations = glossary_entries[term]
            f.write('{0};{1}\n'.format(term.encode('utf-8'),
                    translations[0].translation.encode('utf-8')))

        f.close()


    def get_terms_from_sources_not_used(self, reference_sources, terms):
        not_used = reference_sources.get_terms_not_used_from_references(terms)

        html = u''
        for reference in not_used:

            html += u'<p><b>Termes no usats de la font {0}</b></p>'.format(reference.name)
            html += u'<table border="1" cellpadding="5px" cellspacing="5px" style="border-collapse:collapse;">\r'
            html += u'<tr>\r'
            html += u'<th>Terme</th>\r'
            html += u'</tr>\r'

            terms = sorted(reference.terms.iterkeys())
            for term in terms:
                html += u"<tr>\r"
                html += u'<td>{0}</td>'.format(cgi.escape(term))
                html += u"</tr>\r"

            html += u'</table>'

        return html

    def create(self, html_file, html_comment, corpus, glossary_entries, reference_sources):
        f = open(html_file, 'w')

        f.write(u'<html><head>\n')
        f.write(u'<meta http-equiv="content-type" content="text/html; charset=UTF-8">')
        html = ''

        html += u'<p><b>Comentaris</b></p><ul>'
        html += u'<li>Glossari generat computacionalment al final del mateix hi ha dades sobre la generació.</li>'
        html += u'<li>La columna opcions considerades indica quines altres traduccions apareixen per aquest terme i s\'han considerat.</li>'
        html += u'<li>La columna català és l\'opció més comuna.</li>'
        html += u'<li>Usada indica el % d\'ús respecte a altres opcions i coincidències els cops que s\'ha trobat.</li>'
        html += u'<li>(r) indica el terme es troba a l\'últim Recull de termes publicat.</li>'
        html += u'<li>(m) indica el terme es troba a la terminologia de Microsoft.</li>'
        html += u'<li>(t) indica el terme es troba a la terminologia del TERMCAT.</li>'
        html += u'</ul>'

        html += u'<table border="1" cellpadding="5px" cellspacing="5px" style="border-collapse:collapse;">\r'
        html += u'<tr>\r'
        html += u'<th>#</th>\r'
        html += u'<th>Anglès</th>\r'
        html += u'<th>Català</th>\r'
        html += u'<th>Opcions considerades</th>\r'
        html += '</tr>\r'
        f.write(html.encode('utf-8'))

        references = reference_sources.references
        item = 0

        reference_matches = {}
        for reference in references:
            reference_matches[reference.name] = ReferenceMatches()

        words_cnt = [0, 0, 0]
        for term in glossary_entries:

            sources = ' '
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
                options += u'<p>- {0} (usada {1}%, coincidències {2})</p>\n'.format(cgi.escape(translation.translation),
                           translation.percentage, translation.frequency)

            html = u"<tr>\r"
            html += u'<td>{0}</td>'.format(item)
            html += u'<td>{0}{1}</td>'.format(cgi.escape(term), sources)
            html += u'<td>{0}</td>'.format(cgi.escape(translations[0].translation))
            html += u'<td>{0}</td>'.format(options)
            html += u"</tr>\r"
            f.write(html.encode('utf-8'))

            word_len = len(term.split(' '))
            if word_len <= 3:
                words_cnt[word_len - 1] += 1

        f.write('</table>\n')

        html = self.get_terms_from_sources_not_used(reference_sources, corpus.source_words)
        f.write(html.encode('utf-8'))

        html = u'<p>Data de generació: {0}</p>'.format(datetime.date.today().strftime("%d/%m/%Y"))
        html += '<p>Cadenes analitzades: {0}</p>'.format(corpus.strings)
        html += '<p>Cadenes seleccionades: {0} - {1}%</p>'. \
                format(corpus.strings_selected,
                       100 * corpus.strings_selected / corpus.strings)
        html += u'<p>Termes únics totals selecionats: {0}</p>'. \
                format(len(corpus.source_words))
        html += u'<p><b>Mesures de qualitat</b></p>'

        for name in reference_matches.keys():
            match = reference_matches[name]
            html += u'<p>Dels 50 primers termes quants eren al {0}: {1}% ({2})</p>'. \
                    format(name, match.first_50 * 100 / 50, match.first_50)
            html += u'<p>Dels 100 primers termes quants eren al {0}: {1}% ({2})</p>'. \
                    format(name, match.first_100 * 100 / 100, match.first_100)
            html += u'<p>Dels 500 primers termes quants eren al {0}: {1}% ({2})</p>'. \
                    format(name, match.first_500 * 100 / 500, match.first_500)
            html += u'<p>Dels 2000 primers termes quants eren al {0}: {1}% ({2})</p>'. \
                    format(name, match.first_2000 * 100 / 2000, match.first_2000)

        html += u'<p>{0} cadenes amb 1 paraula, {1} cadenes amb 2 paraules, {2}'\
                 ' cadenes amb 3 paraules</p>'.format(words_cnt[0], words_cnt[1], words_cnt[2])

        if len(html_comment) > 0:
            comment = unicode(html_comment, "UTF-8")  # utf-8 is the system encoding
            html += u"Comentari de generació: " + comment

        f.write(html.encode('utf-8'))

        f.write('</head></html>\n')
        f.close()

        self.create_text_dump(corpus.documents, glossary_entries, reference_sources)
