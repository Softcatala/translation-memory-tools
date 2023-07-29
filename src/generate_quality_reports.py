#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017-2021 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import os
import time
import yaml
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from collections import OrderedDict
from optparse import OptionParser
from builder.findfiles import FindFiles
from builder.jsonbackend import JsonBackend
from quality.report import Report
from quality.languagetool import LanguageTool
from quality.pototext import PoToText

class GenerateQualityReports():

    def init_logging(self, del_logs):
        logfile = 'generate_quality_reports.log'
        logfile_error = 'generate_quality_reports-error.log'

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

    def read_parameters(self):
        parser = OptionParser()

        defaut_dir = os.path.join(os.getcwd(), "output/individual_pos/")
        parser.add_option(
            "-s",
            "--source",
            action="store",
            type="string",
            dest="source_dir",
            default=defaut_dir,
            help="Source directory of po files")

        (options, args) = parser.parse_args()

        if len(options.source_dir) == 0:
            parser.print_help()
            exit(1)

        return options.source_dir


    def read_config(self):
        SECTION_LT = "lt"
        SECTION_POLOGY = "pology"

        lt = OrderedDict()
        pology = OrderedDict()

        with open('../cfg/quality/parameters.yaml', 'r') as f:
            doc = yaml.load(f, Loader=yaml.FullLoader)
            for dictionaries in doc[SECTION_LT]:
                for k in dictionaries.keys():
                    lt[k] = dictionaries[k]

            for dictionaries in doc[SECTION_POLOGY]:
                for k in dictionaries.keys():
                    pology[k] = dictionaries[k]

        return lt, pology

    def run_pology(self, pology, po_transonly, html):
        posieve = pology['posieve']

        cmd = pology['header-fix'].format(posieve, po_transonly)
        os.system(cmd)

        rules = ''
        for rule in pology['rules']:
            if '/' not in rule:
                rules = rules + ' -s rfile:{0}{1}'.format(pology['rules-dir'], rule)
            else:
                rules = rules + ' -s rfile:{0}'.format(rule)

        cmd = pology['command'].format(posieve, rules, po_transonly, html)
        exit_code = os.system(cmd)
        if exit_code != 0:
            logging.info(f"run_pology. Exit error: {exit_code}. Cmd: '{cmd}'")

    def load_projects_ids_from_json(self):
        projects = []
        projects_dir = '../cfg/projects/'
        json = JsonBackend(projects_dir)
        json.load()

        for project_dto in json.projects:
            if project_dto.quality_report is False:
                print("Skipping quality generation for: " + project_dto.name)
                continue

            projects.append(project_dto.project_id)

        return projects

    def generate_report(self, source_dir):

        lt, pology = self.read_config()
        logging.info("Source directory: " + source_dir)

        report_filename = os.path.basename(os.path.normpath(source_dir)) + ".html"

        report = Report()
        languagetool = LanguageTool(lt)
        report.create_project_report(lt['lt-html-dir'],
                                     lt['lt_output'],
                                     report_filename,
                                     languagetool._get_lt_version())

        for po_file in FindFiles().find_recursive(source_dir, "*.po"):
            txt_file = po_file + ".txt"
            json_file = po_file + ".json"
            po_transonly = po_file + "-translated-only.po"
            pology_report = po_file + "-pology.html"
            file_report = po_file + "-report.html"

            start_time = time.time()
            poTotext = PoToText()
            rslt = poTotext.write_text_file(po_file, po_transonly, txt_file)
            if not rslt:
                continue

            if os.stat(txt_file).st_size == 0:
                logging.info("No translations in file:" + txt_file)
                continue

            start_time = time.time()
            languagetool.run_lt(lt, txt_file, json_file)
            po_file_logname = po_file[len(source_dir) + 1:]
            logging.debug("LT runned PO {0} - {1:.2f}s".format(po_file_logname, time.time() - start_time))

            start_time = time.time()
            languagetool.generate_lt_report(lt['lt-html-dir'], json_file, file_report)

            if os.path.isfile(file_report):
                report.add_file_to_project_report(file_report)
            else:
                logging.error("Unable to add:" + file_report)
                continue

            start_time = time.time()
            self.run_pology(pology, po_transonly, pology_report)
            logging.debug("Pology runned PO {0} - {1:.2f}s".format(po_file_logname, time.time() - start_time))

            if os.path.isfile(pology_report):
                report.add_file_to_project_report(pology_report)
                os.remove(pology_report)
            else:
                report.add_string_to_project_report('El Pology no ha detectat cap error.')

            os.remove(txt_file)
            os.remove(json_file)
            os.remove(po_transonly)
            os.remove(file_report)

        footer_filename = os.path.join(lt['lt-html-dir'], "footer.html")
        report.add_file_to_project_report(footer_filename)
        report.close()

    def main(self):
        print("Quality report generator")
        self.init_logging(True)

        total_start_time = datetime.datetime.now()
        projects = self.load_projects_ids_from_json()
        source_dir = self.read_parameters()
        logging.debug(f"Root source_dir {source_dir}")
        # The number of processess to use is calculated by Python taking into account number of cpus
        with ThreadPoolExecutor() as executor:
            for project in projects:
                executor.submit(self.generate_report, os.path.join(source_dir, project))

        s = 'Time used to generate quality reports: {0}'.format(datetime.datetime.now() - total_start_time)
        logging.info(s)

if __name__ == "__main__":
    generate = GenerateQualityReports()
    generate.main()
