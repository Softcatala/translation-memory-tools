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

import datetime


class Glossary(object):
    """Represents all the data need to generate a glossary."""

    def __init__(self, description=""):
        self.date = datetime.date.today().strftime("%d/%m/%Y")
        self.entries = []
        self.description = description

    def get_dict(self):
        entries = []

        for entry in self.entries:
            entries.append(entry.get_dict())

        return {
            "entries": entries,
            "num_of_entries": len(entries),
            "date": self.date,
            "description": self.description,
        }
