# -*- coding: utf-8 -*-
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

from terminology.corpus import Corpus
from io import StringIO
import unittest


class TestCorpus(unittest.TestCase):
    def test_clean_strings(self):
        corpus = Corpus("")
        assert corpus._clean_string("_Hard Disk") == "hard disk"
        assert corpus._clean_string("Contrasen&ya:") == "contrasenya"
        assert corpus._clean_string("All ~Pages") == "all pages"
        assert corpus._clean_string("Properties...") == "properties"

    def test_should_select_string_notags(self):
        corpus = Corpus("")
        assert not corpus._should_select_string(
            "<b>_User name</b>", "<b>_Nom d'usuari</b>"
        )
        assert corpus._should_select_string("User name", "_Nom d'usuari")

    def test_should_select_string_nospaces(self):
        corpus = Corpus("")
        assert not corpus._should_select_string(
            "accessibility;development;test;", "accessibility;development;test;"
        )

    def test_should_select_string_noformatters(self):
        corpus = Corpus("")
        assert not corpus._should_select_string("Usage: %s", "Ús: %s")
        assert corpus._should_select_string("Usage: sample", "Ús: exemple")

    def test_should_select_string_nonumericalonly(self):
        corpus = Corpus("")
        assert not corpus._should_select_string("10", "10")
        assert corpus._should_select_string("10 minutes ago", "Fa 10 minuts")

    def test_should_select_string_empty_target(self):
        corpus = Corpus("")
        assert corpus._should_select_string("This week", "Aquesta setmana")
        assert not corpus._should_select_string("This week", "")

    def test_read_stop_words(self):
        corpus = Corpus("")
        stopwords_file = StringIO("translator-credits")

        assert corpus._should_select_string("translator-credits", "user@test.com")
        corpus._read_stop_words(stopwords_file)
        assert not corpus._should_select_string("translator-credits", "user@test.com")

    def test_should_not_select_parentesis_only(self):
        corpus = Corpus("")
        assert not corpus._should_select_string("()", "()")

    def test_clean_localized(self):
        corpus = Corpus("")
        assert corpus._clean_localized("accès") == "accès"
        assert corpus._clean_localized("àíóè’") == "àíóè'"


if __name__ == "__main__":
    unittest.main()
