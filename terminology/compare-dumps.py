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
from collections import OrderedDict

class DumpEntry:

    def _init__(self):
        self.target = None          

class Dump:

    def __init__(self):
        # key text -> 
        self.entries = OrderedDict()

    def read(self, filename):

        _file = open(filename)

        lines = 0   
        while True:
            line = _file.readline()
            if not line:
                break

            columns = line.split(';')

            if len(columns) != 2:
                #print "Skipping: " + line
                continue

            #if lines > 50:
            #    break

            lines += 1
            dump_entry = DumpEntry()
            dump_entry.target = columns[1] 
            self.entries[columns[0]] = dump_entry

    def compare(self, dump):
        # Missing terms
        items = 0
        MAX = 100
        
        reduced = OrderedDict()
        items = 0
        for i in dump.entries:
            reduced[i] = dump.entries[i]
            items += 1
            if items > MAX:
                break
      
        items = 0
        for entry in self.entries:
            if entry not in reduced:
                print u" " + unicode(entry, "utf-8")

            items += 1
            if items > MAX:
                break

def main():
    
    print "Compare terminology dumps"
    print "Use --help for assistance"

    new = Dump()
    new.read('glossary.txt')
    old = Dump()
    old.read('glossary-old.txt')

    print "New items"
    new.compare(old)
  
    print "Old items"
    old.compare(new)
 
if __name__ == "__main__":
    main()

