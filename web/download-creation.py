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
import locale
sys.path.append('../src/')
from jsonbackend import JsonBackend
import os
import datetime
from optparse import OptionParser
from pofile import POFile
from projectmetadatadao import ProjectMetaDataDao

import pystache


po_directory = None
tmx_directory = None
out_directory = None


class TranslationMemory(object):

    def __init__(self):
        self.name = None
        self.projectweb = None
        self.po_file_text = None
        self.tmx_file_text = None
        self.po_file_link = None
        self.tmx_file_link = None
        self.words = None
        self.last_fetch = None
        self.last_translation_update = None


def link(text, link):
    html = '<a href="' + link + '">'
    html += text + '</a>'
    return html


def get_subdir():
    return "memories/"


def get_path_to_po(po_file):
    return os.path.join(get_subdir(), po_file)


def get_path_to_tmx(po_file):
    filename, file_extension = os.path.splitext(po_file)
    tmxfile = filename + ".tmx"
    return os.path.join(get_subdir(), tmxfile)


def get_tmx_file(po_file):
    filename, file_extension = os.path.splitext(po_file)
    tmxfile = filename + ".tmx"
    return tmxfile


def get_zip_file(filename):
    return filename + ".zip"


def convert_date_to_string(date):
    return date.strftime("%d/%m/%Y")


def get_file_date(filename):
    full_path = os.path.join(po_directory, filename)
    last_ctime = datetime.date.fromtimestamp(os.path.getctime(full_path))
    last_date = last_ctime.strftime("%d/%m/%Y")
    return last_date


def get_project_dates(name):
    project_dao = ProjectMetaDataDao()
    project_dao.open('../src/statistics.db3')
    dto = project_dao.get(name)

    if dto is None:
        last_fetch = ''
        last_translation = ''
    else:
        last_fetch = convert_date_to_string(dto.get_last_fetch())
        last_translation = convert_date_to_string(dto.get_last_translation_update())

    return last_fetch, last_translation


def propulate_project_links(translation_memory, filename):
    potext = filename
    pofile = get_zip_file(get_path_to_po(potext))
    tmxtext = get_tmx_file(potext)
    tmxfile = get_zip_file(get_path_to_tmx(potext))

    translation_memory.po_file_text = get_zip_file(potext)
    translation_memory.po_file_link = pofile
    translation_memory.tmx_file_text = get_zip_file(tmxtext)
    translation_memory.tmx_file_link = tmxfile


def build_all_projects_memory(json, memories):
    '''Builds zip file that contains all memories for all projects'''
    name = u'Totes les memòries de tots els projectes'
    filename = 'tots-tm.po'

    words = get_words(filename)

    if words is None:
        return

    potext = filename
    translation_memory = TranslationMemory()
    translation_memory.words = locale.format("%d", words, grouping=True)

    propulate_project_links(translation_memory, filename)
    translation_memory.name = name
    date = get_file_date(potext)
    translation_memory.last_fetch = date
    translation_memory.last_translation_update = date
    memories.append(translation_memory)

    create_zipfile(po_directory, filename)
    create_zipfile(tmx_directory, get_tmx_file(filename))

    projects = sorted(json.projects, key=lambda x: x.name.lower())
    for project_dto in projects:
        if project_dto.downloadable is True:
            update_zipfile(po_directory, filename, project_dto.filename)
            update_zipfile(tmx_directory, get_tmx_file(filename),
                           get_tmx_file(project_dto.filename))


def build_all_softcatala_memory(json, memories):
    '''Builds zip file that contains all memories for the Softcatalà projects'''
    name = u'Totes les memòries de projectes de Softcatalà'
    filename = 'softcatala-tm.po'

    words = get_words(filename)

    if words == None:
        return

    translation_memory = TranslationMemory()
    translation_memory.words = locale.format("%d", words, grouping=True)
    propulate_project_links(translation_memory, filename)

    translation_memory.name = name
    date = get_file_date(filename)
    translation_memory.last_fetch = date
    translation_memory.last_translation_update = date
    memories.append(translation_memory)

    create_zipfile(po_directory, filename)
    create_zipfile(tmx_directory, get_tmx_file(filename))

    projects = sorted(json.projects, key=lambda x: x.name.lower())
    for project_dto in projects:
        if project_dto.downloadable is True and project_dto.softcatala is True:
            update_zipfile(po_directory, filename, project_dto.filename)
            update_zipfile(tmx_directory, get_tmx_file(filename),
                           get_tmx_file(project_dto.filename))


def get_words(potext):
    full_filename = os.path.join(po_directory, potext)
    words = POFile(full_filename).get_statistics()
    if (words == 0):
        print "Skipping empty translation memory: " + potext
        return None

    return words


def build_invidual_projects_memory(json, memories):
    '''Builds zip file that contains a memory for every project'''
    projects = sorted(json.projects, key=lambda x: x.name.lower())
    for project_dto in projects:
        if project_dto.downloadable is True:
            words = get_words(project_dto.filename)

            if words is None:
                continue

            translation_memory = TranslationMemory()
            translation_memory.words = locale.format("%d", words, grouping=True)

            propulate_project_links(translation_memory, project_dto.filename)

            translation_memory.projectweb = project_dto.projectweb
            translation_memory.name = project_dto.name
            last_fetch, last_translation_update = get_project_dates(project_dto.name)
            translation_memory.last_fetch = last_fetch
            translation_memory.last_translation_update = last_translation_update
            memories.append(translation_memory)

            create_zipfile(po_directory, project_dto.filename)
            create_zipfile(tmx_directory, get_tmx_file(project_dto.filename))


def _process_template(template, filename, variables):
        # Load template and process it
        template = open(template, 'r').read()
        parsed = pystache.Renderer()
        s = parsed.render(unicode(template, "utf-8"), variables)

        # Write output
        f = open(filename, 'w')
        f.write(s.encode("utf-8"))
        f.close()


def process_projects():
    json = JsonBackend("../src/projects.json")
    json.load()

    variables = {}
    memories = []

    build_all_projects_memory(json, memories)
    build_all_softcatala_memory(json, memories)
    build_invidual_projects_memory(json, memories)

    today = datetime.date.today()
    variables['generation_date'] = today.strftime("%d/%m/%Y")
    variables['memories'] = memories
    _process_template("download.mustache", "download.html", variables)


def update_zipfile(src_directory, filename, file_to_add):
    srcfile = os.path.join(src_directory, file_to_add)
    zipfile = os.path.join(out_directory,  get_subdir(), get_zip_file(filename))

    if not os.path.exists(srcfile):
        print 'File {0} does not exists and cannot be zipped'.format(srcfile)
        return

    cmd = 'zip -j {0} {1}'.format(zipfile, srcfile)
    os.system(cmd)


def create_zipfile(src_directory, filename):
    srcfile = os.path.join(src_directory, filename)
    zipfile = os.path.join(out_directory,  get_subdir(), get_zip_file(filename))

    if not os.path.exists(srcfile):
        print 'File {0} does not exists and cannot be zipped'.format(srcfile)
        return

    if os.path.isfile(zipfile):
        os.remove(zipfile)

    cmd = 'zip -j {0} {1}'.format(zipfile, srcfile)
    os.system(cmd)


def read_parameters():
    global po_directory
    global tmx_directory
    global out_directory

    parser = OptionParser()

    parser.add_option("-d", "--podir",
                      action="store", type="string", dest="po_directory",
                      default="../src/",
                      help="Directory to find the PO files")

    parser.add_option("-t", "--tmxdir",
                      action="store", type="string", dest="tmx_directory",
                      default="../src/",
                      help="Directory to find the TMX files")

    parser.add_option("-o", "--ouputdir",
                      action="store", type="string", dest="out_directory",
                      default="",
                      help="Directory to output the files")

    (options, args) = parser.parse_args()

    po_directory = options.po_directory
    tmx_directory = options.tmx_directory
    out_directory = options.out_directory


def create_output_dir(subdirectory):
    directory = os.path.join(out_directory, subdirectory)
    if not os.path.exists(directory):
        os.mkdir(directory)


def main():
    '''
        Reads the projects and generates an HTML to enable downloading all
        the translation memories
    '''
    print "Creates download.html file"
    print "Use --help for assistance"

    try:
        locale.setlocale(locale.LC_ALL, '')
    except Exception as detail:
        print "Exception: " + str(detail)

    read_parameters()
    create_output_dir("memories")
    download = os.path.join(out_directory, "download.html")
    process_projects()


if __name__ == "__main__":
    main()
