#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2013-2014 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import pystache


class UserGlossarySerializer():

    def _create(self, template, filename, glossary_entries, reference_sources):
        # Load template and process it
        template = open(template, 'r').read()
        parsed = pystache.Renderer()
        s = parsed.render(unicode(template, "utf-8"), glossary_entries)

        # Write output
        f = open(filename, 'w')
        f.write(s.encode("utf-8"))
        f.close()

    def create(self, filename, glossary_entries, reference_sources):
        self._create('userglossary-html.mustache', filename + ".html",
                     glossary_entries, reference_sources)
        self._create('userglossary-csv.mustache', filename + ".csv",
                     glossary_entries, reference_sources)
