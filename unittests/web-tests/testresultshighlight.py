#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import unittest

sys.path.append('../web/')
from resultshighlight import ResultsHighlight


class TestResultsHighlight(unittest.TestCase):

    def test_get_simple(self):
        result = ResultsHighlight.get(u"Unselec_t all",  # source
            u'unselect all',  # clean
            u"un<b class = 'match term1'>sel</b>ect all")  #clean_highlighted

        assert result == "Un<b class = 'match term1'>sel</b>ect all"
    
    def test_get_multiple_highlights(self):
        result = ResultsHighlight.get(u"Select &All",  # source
            u'select all',  # clean
            u'<b class="match term0">select</b> <b class="match term1">all</b>')  #clean_highlighted

        assert result == '<b class="match term0">Select</b> <b class="match term1">&All</b>'


if __name__ == '__main__':
    unittest.main()
