#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2014 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from whoosh.analysis import *
from whoosh.fields import *


def get_clean_string(result):
    CHARS = ('_', '&', '~')  # Accelerators.
    for char in CHARS:
        result = result.replace(char, '')

    return result.lower()


class CleanUpFilter(Filter):
    """Clean up accelerators when generating the tokens for the index
        allowing to ignore them.
    """
    def __call__(self, tokens):
        for t in tokens:
            t.text = get_clean_string(t.text)
            yield t
