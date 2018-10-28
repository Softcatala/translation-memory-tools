#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import logging
import os
import datetime
from optparse import OptionParser

from builder.jsonbackend import JsonBackend
from builder.projects import Projects


projects = Projects()


def init_logging(del_logs):
    logfile = 'builder.log'
    logfile_error = 'builder-error.log'

    if del_logs and os.path.isfile(logfile):
        os.remove(logfile)

    if del_logs and os.path.isfile(logfile_error):
        os.remove(logfile_error)

    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    logger = logging.getLogger('')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    fh = logging.FileHandler(logfile_error)
    fh.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def read_parameters():
    parser = OptionParser()

    parser.add_option(
        '-d',
        '--del-logs',
        action='store_true',
        dest='del_logs',
        default=False,
        help='Delete previous existing logs'
    )

    parser.add_option(
        '-n',
        '--no-source',
        action='store_false',
        dest='add_source',
        default=True,
        help='Do not include the source for the translation segment'
    )

    parser.add_option(
        '-p',
        '--projects',
        action='store',
        type='string',
        dest='projects_names',
        default='',
        help='To restrict the processing of projects to comma separated '
        'given list e.g.: (fedora, ubuntu)'
    )

    parser.add_option(
        '-s',
        '--json',
        action='store',
        type='string',
        dest='projects_dir',
        default='../cfg/projects/',
        help="Define the directory that contains the json files with the "
        "project's definitions"
    )

    parser.add_option(
        '-a',
        '--all',
        action='store_true',
        dest='only_all_projects_tm',
        default=False,
        help='Looks for already existing PO files in the current directory '
        'and creates a new tm.po with all memories'
    )

    parser.add_option(
        '-c',
        '--softcatala',
        action='store_true',
        dest='softcatala_only',
        default=False,
        help=u'Process only Softcatalà memories'
    )

    parser.add_option(
        "-o",
        "--outputdir",
        action="store",
        type="string",
        dest="out_directory",
        default="output/",
        help="Directory to output the files")

    (options, args) = parser.parse_args()

    projects_names = ''
    if options.projects_names:
        projects_names = options.projects_names.split(',')

    return (options.add_source, projects_names, options.projects_dir,
            options.only_all_projects_tm, options.softcatala_only,
            options.out_directory, options.del_logs)


def load_projects_from_json(add_source, projects_names, projects_dir,
                            softcatala_only):
    json = JsonBackend(projects_dir)
    json.load()

    msg = 'Projects defined in the projects configuration directory {0}'.format(len(json.projects))
    logging.info(msg)
    for project_dto in json.projects:
        project_dto_lower = project_dto.name.lower().strip()

        if softcatala_only and not project_dto.softcatala:
            continue

        if projects_names:
            found = False
            for project_name in projects_names:
                if project_name.lower().strip() == project_dto_lower:
                    found = True

            if not found:
                continue

        projects.add_project(project_dto, add_source)


def create_output_dir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)

if __name__ == '__main__':
    print('Translation memory builder version 0.1')
    print('Use --help for assistance')

    start_time = datetime.datetime.now()
    (add_source, projects_names, projects_dir, only_all_projects_tm,
     softcatala_only, out_directory, del_logs) = read_parameters()

    init_logging(del_logs)
    projects.set_out_directory(out_directory)
    create_output_dir(out_directory)

    load_projects_from_json(add_source, projects_names, projects_dir,
                            softcatala_only)

    if only_all_projects_tm:
        projects.create_tm_for_all_projects()
    elif softcatala_only:
        projects.set_tm_file('softcatala-tm.po')
        projects.create_tm_for_all_projects()
    else:
        projects()

    projects.to_tmx()
    projects.statistics()

    s = 'Time used to build memories: {0}'.format(datetime.datetime.now() - start_time)
    logging.info(s)
