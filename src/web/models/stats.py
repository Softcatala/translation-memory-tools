#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import json

sys.path.append('../')
sys.path.append('../builder')

from builder.projectmetadatadao import ProjectMetaDataDao

class Stats(object):

    def get_json(self):
        dao = ProjectMetaDataDao()
        dao.open('statistics.db3')
        total_words = 0
        projects = dao.get_all()
        for project in projects:
            total_words += project.words

        results = {}
        results['total_words'] = total_words
        results['projects'] = len(projects)
        return json.dumps(results, indent=4, separators=(',', ': '))
