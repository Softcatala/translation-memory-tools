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

import datetime

class ProjectMetaDataDto:

    def __init__(self, name):
        self.name = name
        self._last_translation_update = None 
        self._last_fetch = None
        self.words = 0
        self.checksum = ''

    def get_last_translation_update(self):
        return self._last_translation_update

    def set_last_translation_update(self, value):
        if not isinstance(value, datetime.datetime):
            raise TypeError("Property must be set to a datetime. Type:" 
                            + str(type(value)))

        self._last_translation_update = value


    last_translation_update = property(get_last_translation_update, 
                                      set_last_translation_update)

    
    def get_last_fetch(self):
        return self._last_fetch

    def set_last_fetch(self, value):
        if not isinstance(value, datetime.datetime):
            raise TypeError("Property must be set to a datetime. Type:" 
                            + str(type(value)))

        self._last_fetch = value

    _last_fetch = property(get_last_fetch, set_last_fetch)

  
    def __str__(self):

        text = 'ProjectMetaDataDto. Name: {0}, last_translation_update: {1}, ' \
            'last_fetch: {2}, words {3}'

        return text.format(self.name, self._last_translation_update, 
                          self._last_fetch, self.words)
   
