#!/usr/bin/env python3
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

import datetime
import locale
import os
import json

from optparse import OptionParser
from builder.jsonbackend import JsonBackend
from builder.pofile import POFile
from builder.projectmetadatadao import ProjectMetaDataDao
from builder.licenses import Licenses

static_host = "https://static.softcatala.org/"


def json_remove_unncessary_fields(ctx):
    memories = ctx["memories"]
    for memory in memories:
        if memory["quality_report"] is False:
            memory["quality_file_link"] = ""

        del memory["quality_report"]


def write_download_json(ctx):
    json_remove_unncessary_fields(ctx)
    content = json.dumps(ctx, indent=4, separators=(",", ": "))
    with open("projects.json", "w") as file:
        file.write(content)


class TranslationMemory(dict):
    def _get_license_link(self, license):
        links = Licenses().get_licenses_name_and_link()
        values = links.get(license)
        if values is None:
            return ""
        else:
            return values["link"]

    def __init__(
        self,
        words=None,
        name=None,
        last_fetch=None,
        last_translation_update=None,
        projectweb=None,
        filename=None,
        quality_report=True,
        license="",
        project_id="",
    ):
        self.__setitem__("name", name)
        self.__setitem__("project_id", project_id)
        self.__setitem__("projectweb", projectweb)

        if license == Licenses().PROPIETARY:
            self.__setitem__("po_file_text", "")
            self.__setitem__("po_file_link", "")
            self.__setitem__("tmx_file_text", "")
            self.__setitem__("tmx_file_link", "")
        else:
            self.__setitem__("po_file_text", get_zip_file(filename))
            self.__setitem__("po_file_link", get_zip_file(get_link_to_po(filename)))
            self.__setitem__("tmx_file_text", get_zip_file(get_tmx_file(filename)))
            self.__setitem__("tmx_file_link", get_zip_file(get_link_to_tmx(filename)))

        self.__setitem__("quality_file_link", get_link_to_quality_report(project_id))
        self.__setitem__("words", words)
        self.__setitem__("last_fetch", last_fetch)
        self.__setitem__("last_translation_update", last_translation_update)
        self.__setitem__("quality_report", quality_report)
        self.__setitem__("license", license)
        self.__setitem__("license_link", self._get_license_link(license))


def get_link_to_quality_report(name):
    name = name.lower()
    return "{0}quality/{1}.html".format(static_host, name)


def get_subdir():
    return "memories/"


def get_link_to_po(po_file):
    return static_host + os.path.join(get_subdir(), po_file)


def get_link_to_tmx(po_file):
    filename, file_extension = os.path.splitext(po_file)
    tmxfile = filename + ".tmx"
    return static_host + os.path.join(get_subdir(), tmxfile)


def get_tmx_file(po_file):
    filename, file_extension = os.path.splitext(po_file)
    return filename + ".tmx"


def get_zip_file(filename):
    return filename + ".zip"


def get_file_date(filename, po_directory):
    full_path = os.path.join(po_directory, filename)
    last_ctime = datetime.date.fromtimestamp(os.path.getctime(full_path))
    last_date = last_ctime.strftime("%d/%m/%Y")
    return last_date


def get_project_dates(name):
    project_dao = ProjectMetaDataDao()
    project_dao.open("statistics.db3")
    dto = project_dao.get(name)

    if dto is None:
        return "", ""

    last_fetch = dto.last_fetch.strftime("%d/%m/%Y")
    last_translation = dto.last_translation_update.strftime("%d/%m/%Y")
    return last_fetch, last_translation


def get_words(potext, po_directory):
    full_filename = os.path.join(po_directory, potext)
    words = POFile(full_filename).get_statistics()
    if words == 0:
        print("Skipping empty translation memory: " + potext)
        return None

    return words


def build_combined_memory(
    projects,
    memories,
    filename,
    name,
    project_id,
    po_directory,
    tmx_directory,
    out_directory,
):
    """Build zip file containing all memories for the specified projects."""
    words = get_words(filename, po_directory)

    if words is None:
        return

    date = get_file_date(filename, po_directory)

    translation_memory = TranslationMemory(
        words=locale.format("%d", words, grouping=True),
        name=name,
        project_id=project_id,
        last_fetch=date,
        last_translation_update=date,
        filename=filename,
        license="GPL-3.0-only",
        quality_report=False,
    )
    memories.append(translation_memory)

    create_zipfile(po_directory, filename, out_directory)
    create_zipfile(tmx_directory, get_tmx_file(filename), out_directory)

    for project_dto in projects:
        if project_dto.license == Licenses().PROPIETARY:
            continue

        update_zipfile(po_directory, filename, project_dto.filename, out_directory)
        update_zipfile(
            tmx_directory,
            get_tmx_file(filename),
            get_tmx_file(project_dto.filename),
            out_directory,
        )


def build_invidual_projects_memory(
    projects, memories, po_directory, tmx_directory, out_directory
):
    """Build zip file that contains a memory for every project."""
    for project_dto in projects:
        words = get_words(project_dto.filename, po_directory)

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
            license=project_dto.license,
            quality_report=project_dto.quality_report,
            project_id=project_dto.project_id,
        )
        memories.append(translation_memory)

        create_zipfile(po_directory, project_dto.filename, out_directory)
        create_zipfile(tmx_directory, get_tmx_file(project_dto.filename), out_directory)


def process_projects(po_directory, tmx_directory, out_directory):
    json = JsonBackend("../cfg/projects/")
    json.load()
    projects = sorted(json.projects, key=lambda x: x.name.lower())

    all_projects = [proj for proj in projects if proj.downloadable]
    softcatala_projects = [proj for proj in all_projects if proj.softcatala]

    memories = []

    build_combined_memory(
        all_projects,
        memories,
        "tots-tm.po",
        "Totes les memòries de tots els projectes",
        "tots",
        po_directory,
        tmx_directory,
        out_directory,
    )

    build_combined_memory(
        softcatala_projects,
        memories,
        "softcatala-tm.po",
        "Totes les memòries de projectes de Softcatalà",
        "softcatala",
        po_directory,
        tmx_directory,
        out_directory,
    )

    build_invidual_projects_memory(
        all_projects, memories, po_directory, tmx_directory, out_directory
    )

    ctx = {
        "generation_date": datetime.date.today().strftime("%d/%m/%Y"),
        "memories": memories,
    }
    write_download_json(ctx)


def update_zipfile(src_directory, filename, file_to_add, out_directory):
    srcfile = os.path.join(src_directory, file_to_add)
    zipfile = os.path.join(out_directory, get_subdir(), get_zip_file(filename))

    if not os.path.exists(srcfile):
        print("File {0} does not exists and cannot be zipped".format(srcfile))
        return

    cmd = 'zip -j "{0}" "{1}"'.format(zipfile, srcfile)
    os.system(cmd)


def create_zipfile(src_directory, filename, out_directory):
    srcfile = os.path.join(src_directory, filename)
    zipfile = os.path.join(out_directory, get_subdir(), get_zip_file(filename))

    if not os.path.exists(srcfile):
        print("File {0} does not exists and cannot be zipped".format(srcfile))
        return

    if os.path.isfile(zipfile):
        os.remove(zipfile)

    cmd = 'zip -j "{0}" "{1}"'.format(zipfile, srcfile)
    os.system(cmd)


def read_parameters():
    parser = OptionParser()

    parser.add_option(
        "-d",
        "--podir",
        action="store",
        type="string",
        dest="po_directory",
        default=".",
        help="Directory to find the PO files",
    )

    parser.add_option(
        "-t",
        "--tmxdir",
        action="store",
        type="string",
        dest="tmx_directory",
        default=".",
        help="Directory to find the TMX files",
    )

    parser.add_option(
        "-o",
        "--outputdir",
        action="store",
        type="string",
        dest="out_directory",
        default="",
        help="Directory to output the files (files will be at 'memories' subdir)",
    )

    (options, args) = parser.parse_args()

    return options.po_directory, options.tmx_directory, options.out_directory


def create_output_dir(subdirectory, out_directory):
    directory = os.path.join(out_directory, subdirectory)
    if not os.path.exists(directory):
        os.mkdir(directory)


def main():
    print(
        "Creates files to be download and projects.json file with all information about projects"
    )
    print("Use --help for assistance")

    try:
        locale.setlocale(locale.LC_ALL, "")
    except Exception as detail:
        print("Exception: " + str(detail))

    po_directory, tmx_directory, out_directory = read_parameters()
    create_output_dir("memories", out_directory)
    process_projects(po_directory, tmx_directory, out_directory)


if __name__ == "__main__":
    main()
