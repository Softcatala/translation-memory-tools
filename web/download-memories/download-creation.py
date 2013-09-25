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
sys.path.append('../../src/')
from jsonbackend import JsonBackend
import os


def link(text, link):
    html = '<a href="' + link + '">'
    html += text + '</a>'
    return html
    
    
def table_row_generate(name, potext, pofile, tmxtext, tmxfile):

    html = "<tr>\r"
    html += "<td>" + name + "</td>\r"
    html += "<td>" + link(potext, pofile) + "</td>\r"
    html += "<td>" + link(tmxtext, tmxfile) + "</td>\r"
    html += "</tr>\r"
    return html
    
    
def table_row(name, potext):

    subdirectory = "memories/"
    
    pofile = os.path.join(subdirectory, potext)
    filename, file_extension = os.path.splitext(potext)
    tmxfile = filename + ".tmx"
    
    return table_row_generate(name, potext, pofile,
                              tmxfile, os.path.join(subdirectory, tmxfile))

def process_projects():

    json = JsonBackend("../../src/projects.json")
    json.load()

    html = '<h1 class ="section">Baixa les memories de traduccio</h1>\r'
    html += '<table border="1" cellpadding="5px" cellspacing="5px" style="border-collapse:collapse;">\r'
    html += '<tr>\r'
    html += '<th>Projecte</th>\r'
    html += '<th>Fitxer PO</th>\r'
    html += '<th>Fitxer TMX</th>\r'
    html += '</tr>\r'

    for project_dto in json.projects:
        if (project_dto.name != 'Header'):    
            html += table_row(project_dto.name, project_dto.filename)

    html += table_row('Totes les memories', 'tm-all.po')
    html += '</table>\r'
    html += '<br/>\r'
    return html


def main():
    '''
        Reads the projects and generates an HTML to enable downloading all
        the translation memories
    '''

    print "Creates download.html file"

    html = process_projects()
    html_file = open("download.html", "w")
    html_file.write(html)
    html_file.close()

if __name__ == "__main__":
    main()
