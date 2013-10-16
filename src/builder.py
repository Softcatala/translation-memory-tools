#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from jsonbackend import JsonBackend
from optparse import OptionParser
from projects import Projects

import logging
import os
import time


projects = Projects('tm.po')
add_source = True
projects_names = None
projects_json = 'projects.json'
only_all_projects_tm = None
softcatala_only = None


def init_logging():
    logfile = 'builder.log'

    if os.path.isfile(logfile):
        os.remove(logfile)

    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    logger = logging.getLogger('')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)


def read_parameters():
    global add_source
    global projects_names
    global projects_json
    global only_all_projects_tm
    global softcatala_only

    parser = OptionParser()

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
        help='To restrict the processing of projects to comma separated '
        'given list e.g.: (fedora, ubuntu)'
    )

    parser.add_option(
        '-s',
        '--json',
        action='store',
        type='string',
        dest='projects_json',
        help="Define the json file contains the project's definitions "
        "(default: projects.json)"
    )

    parser.add_option(
        '-a',
        '--all',
        action='store_true',
        dest='only_all_projects_tm',
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

    (options, args) = parser.parse_args()

    add_source = options.add_source

    if options.projects_json is not None:
        projects_json = options.projects_json

    if options.projects_names is not None:
        projects_names = options.projects_names.split(',')

    only_all_projects_tm = options.only_all_projects_tm
    softcatala_only = options.softcatala_only

def load_projects_from_json():
    json = JsonBackend(projects_json)
    json.load()
    
    global softcatala_only

    msg = 'Projects defined in json file {0}'.format(len(json.projects))
    logging.info(msg)
    for project_dto in json.projects:
        project_dto_lower = project_dto.name.lower().strip()
        
        if softcatala_only is True and len(project_dto.softcatala) == 0:
            continue

        if projects_names:
            found = False
            for project_name in projects_names:
                if project_name.lower().strip() == project_dto_lower:
                    found = True

            if not found:
                continue

        projects.add_project(project_dto, add_source)


if __name__ == '__main__':
    print 'Translation memory builder version 0.1'
    print 'Use --help for assistance'

    start_time = time.time()
    init_logging()
    read_parameters()
    load_projects_from_json()

    if only_all_projects_tm:
        projects.create_tm_for_all_projects()
    elif softcatala_only:
        projects.set_tm_file('softcatala-tm.po')
        projects.create_tm_for_all_projects()
    else:
        projects()

    projects.to_tmx()
    projects.statistics()

    s = 'Execution time: {0} seconds'.format(str(time.time() - start_time))
    logging.info(s)
