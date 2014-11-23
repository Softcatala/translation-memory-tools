#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2013 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import sys
import locale
sys.path.append('../builder')
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

    def __init__(self, words=None, name=None, last_fetch=None,
                 last_translation_update=None, projectweb=None, filename=None):
        self.name = name
        self.projectweb = projectweb
        self.po_file_text = get_zip_file(filename)
        self.po_file_link = get_zip_file(get_path_to_po(filename))
        self.tmx_file_text = get_zip_file(get_tmx_file(filename))
        self.tmx_file_link = get_zip_file(get_path_to_tmx(filename))
        self.words = words
        self.last_fetch = last_fetch
        self.last_translation_update = last_translation_update


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
    return filename + ".tmx"


def get_zip_file(filename):
    return filename + ".zip"


def get_file_date(filename):
    full_path = os.path.join(po_directory, filename)
    last_ctime = datetime.date.fromtimestamp(os.path.getctime(full_path))
    last_date = last_ctime.strftime("%d/%m/%Y")
    return last_date


def get_project_dates(name):
    project_dao = ProjectMetaDataDao()
    project_dao.open('../builder/statistics.db3')
    dto = project_dao.get(name)

    if dto is None:
        return '', ''

    last_fetch = dto.last_fetch.strftime("%d/%m/%Y")
    last_translation = dto.last_translation_update.strftime("%d/%m/%Y")
    return last_fetch, last_translation


def build_all_projects_memory(json, memories):
    """Build zip file that contains all memories for all projects."""
    filename = 'tots-tm.po'

    words = get_words(filename)

    if words is None:
        return

    date = get_file_date(filename)

    translation_memory = TranslationMemory(
        words=locale.format("%d", words, grouping=True),
        name=u'Totes les memòries de tots els projectes',
        last_fetch=date,
        last_translation_update=date,
        filename=filename,
    )
    memories.append(translation_memory)

    create_zipfile(po_directory, filename)
    create_zipfile(tmx_directory, get_tmx_file(filename))

    projects = sorted(json.projects, key=lambda x: x.name.lower())
    for project_dto in projects:
        if project_dto.downloadable:
            update_zipfile(po_directory, filename, project_dto.filename)
            update_zipfile(tmx_directory, get_tmx_file(filename),
                           get_tmx_file(project_dto.filename))


def build_all_softcatala_memory(json, memories):
    """Build zip file containing all memories for all Softcatalà projects."""
    filename = 'softcatala-tm.po'

    words = get_words(filename)

    if words == None:
        return

    date = get_file_date(filename)

    translation_memory = TranslationMemory(
        words=locale.format("%d", words, grouping=True),
        name=u'Totes les memòries de projectes de Softcatalà',
        last_fetch=date,
        last_translation_update=date,
        filename=filename,
    )
    memories.append(translation_memory)

    create_zipfile(po_directory, filename)
    create_zipfile(tmx_directory, get_tmx_file(filename))

    projects = sorted(json.projects, key=lambda x: x.name.lower())
    for project_dto in projects:
        if project_dto.downloadable and project_dto.softcatala:
            update_zipfile(po_directory, filename, project_dto.filename)
            update_zipfile(tmx_directory, get_tmx_file(filename),
                           get_tmx_file(project_dto.filename))


def get_words(potext):
    full_filename = os.path.join(po_directory, potext)
    words = POFile(full_filename).get_statistics()
    if words == 0:
        print("Skipping empty translation memory: " + potext)
        return None

    return words


def build_invidual_projects_memory(json, memories):
    """Build zip file that contains a memory for every project."""
    projects = sorted(json.projects, key=lambda x: x.name.lower())
    for project_dto in projects:
        if project_dto.downloadable:
            words = get_words(project_dto.filename)

            if words is None:
                continue

            name = project_dto.name
            last_fetch, last_translation_update = get_project_dates(name)

            translation_memory = TranslationMemory(
                words=locale.format("%d", words, grouping=True),
                name=name,
                last_fetch=last_fetch,
                last_translation_update=last_translation_update,
                projectweb=project_dto.projectweb,
                filename=project_dto.filename,
            )
            memories.append(translation_memory)

            create_zipfile(po_directory, project_dto.filename)
            create_zipfile(tmx_directory, get_tmx_file(project_dto.filename))


def process_template(template, filename, ctx):
    # Load template and process it.
    template = open(template, 'r').read()
    parsed = pystache.Renderer()
    s = parsed.render(unicode(template, "utf-8"), ctx)

    # Write output.
    f = open(filename, 'w')
    f.write(s.encode("utf-8"))
    f.close()


def process_projects():
    json = JsonBackend("../builder/projects.json")
    json.load()

    memories = []

    build_all_projects_memory(json, memories)
    build_all_softcatala_memory(json, memories)
    build_invidual_projects_memory(json, memories)

    ctx = {
        'generation_date': datetime.date.today().strftime("%d/%m/%Y"),
        'memories': memories,
    }
    process_template("templates/download.mustache", "download.html", ctx)


def update_zipfile(src_directory, filename, file_to_add):
    srcfile = os.path.join(src_directory, file_to_add)
    zipfile = os.path.join(out_directory,  get_subdir(), get_zip_file(filename))

    if not os.path.exists(srcfile):
        print('File {0} does not exists and cannot be zipped'.format(srcfile))
        return

    cmd = 'zip -j {0} {1}'.format(zipfile, srcfile)
    os.system(cmd)


def create_zipfile(src_directory, filename):
    srcfile = os.path.join(src_directory, filename)
    zipfile = os.path.join(out_directory,  get_subdir(), get_zip_file(filename))

    if not os.path.exists(srcfile):
        print('File {0} does not exists and cannot be zipped'.format(srcfile))
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
                      default="../builder",
                      help="Directory to find the PO files")

    parser.add_option("-t", "--tmxdir",
                      action="store", type="string", dest="tmx_directory",
                      default="../builder",
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
    """Generate an HTML listing all the translation memories.

    Read the projects and generate an HTML to enable downloading all the
    translation memories.
    """
    print("Creates download.html file")
    print("Use --help for assistance")

    try:
        locale.setlocale(locale.LC_ALL, '')
    except Exception as detail:
        print("Exception: " + str(detail))

    read_parameters()
    create_output_dir("memories")
    download = os.path.join(out_directory, "download.html")
    process_projects()


if __name__ == "__main__":
    main()
