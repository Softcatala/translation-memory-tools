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

import datetime
import cgi
from serializer import Serializer

class UserGlossarySerializer(Serializer):

    def create(self, html_file, html_comment, corpus, tfxdf, reference_sources):

        MAX_TERMS = 1000

        _terms = sorted(tfxdf, key=tfxdf.get, reverse=True)
        terms = sorted(_terms[:MAX_TERMS])

        f = open(html_file, 'w')

        f.write(u'<html><head>\n')
        f.write(u'<meta http-equiv="content-type" content="text/html; charset=UTF-8">')
        html = ''

        comment = unicode(html_comment, "UTF-8")  # utf-8 is the system encoding
        html += u'<p>{0}</p>'.format(comment)
        html += u'<table border="1" cellpadding="5px" cellspacing="5px" style="border-collapse:collapse;">\r'
        html += u'<tr>\r'
        html += u'<th>Anglès</th>\r'
        html += u'<th>Català</th>\r'
        html += u'<th>Opcions considerades</th>\r'
        html += '</tr>\r'
        f.write(html.encode('utf-8'))

        item = 0
        for term in terms:

            item += 1
            translations = self.create_translations_for_word_sorted_by_frequency(corpus.documents, term)

            options = ''
            for translation in translations:
                options += u'<p>- {0} (usada {1}%, coincidències {2})</p>\n'.format(cgi.escape(translation.translation),
                           translation.percentage, translation.frequency)

            html = u"<tr>\r"
            html += u'<td>{0}</td>'.format(cgi.escape(term))
            html += u'<td>{0}</td>'.format(cgi.escape(translations[0].translation))
            html += u'<td>{0}</td>'.format(options)
            html += u"</tr>\r"
            f.write(html.encode('utf-8'))

        f.write('</table>\n')

        html = u'<p>Data de generació: {0}</p>'.format(datetime.date.today().strftime("%d/%m/%Y"))
        f.write(html.encode('utf-8'))

        f.write('</head></html>\n')
        f.close()

