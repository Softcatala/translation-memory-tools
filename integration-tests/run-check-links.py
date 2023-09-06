# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import os
import logging
from urllib.request import Request, urlopen
from urllib.error import HTTPError

sys.path.append('../src/')

from builder.jsonbackend import JsonBackend

TIMEOUT = 10
HTTP_STATUS_CODE_OK = 200
HTTP_STATUS_CODE_NOT_FOUND = 404

def init_logging(del_logs):
    logfile = 'run-check-links.log'
    logfile_error = 'run-check-links-error.log'

    if del_logs and os.path.isfile(logfile):
        os.remove(logfile)

    if del_logs and os.path.isfile(logfile_error):
        os.remove(logfile_error)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    LOGSTDOUT = os.environ.get('LOGSTDOUT', '0')

    if LOGSTDOUT == '0':
        console = logging.StreamHandler() # By default uses stderr
    else:
        console = logging.StreamHandler(stream=sys.stdout)

    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    logger = logging.getLogger('')
    console.setLevel(LOGLEVEL)

    if LOGLEVEL != "INFO":
        console.setFormatter(formatter)

    logger.addHandler(console)

    fh = logging.FileHandler(logfile_error)
    fh.setLevel(logging.ERROR)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

def check_project_link(project_web):
    if project_web is None or len(project_web) == 0:
        return

    code = HTTP_STATUS_CODE_OK
    try:
        req = Request(project_web, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64;) Gecko Firefox'})
        result = urlopen(req)

    except HTTPError as e:
        code = e.code

    except Exception as e:
        code = 0

    if code != HTTP_STATUS_CODE_OK:
        logging.error(f'Project link {project_web} returns {code}')
        return False
    else:
        return True

def check_project_links():
    json = JsonBackend("../cfg/projects/")
    json.load()

    checked = 0
    errors = 0
    for project_dto in json.projects:
        if not project_dto.downloadable:
            continue

        checked += 1
        if not check_project_link(project_dto.projectweb):
            errors += 1

    print(f"Links checked {checked}, with errors {errors}")

if __name__ == '__main__':
    print("Check all projects links to external project webs")

    init_logging(True)
    check_project_links()
