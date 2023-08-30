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

import json
import logging
import re
from collections import OrderedDict
from .findfiles import FindFiles


class ProjectDTO(object):
    def __init__(self, name):
        self.name = name
        self.project_id = self._from_name_to_project_id(name)
        self.filename = self._sanatize_filename("project.project_id-tm.po")
        self.projectweb = ""
        self.softcatala = False
        self.disabled = False
        self.downloadable = True
        self.selectable = True
        self.license = ""
        self.quality_report = True
        self.filesets = []

    def _from_name_to_project_id(self, name):
        name = name.replace(" ", "_")
        return name.lower()

    def _sanatize_filename(self, filename):
        return re.sub(r"[^\.a-zA-Z0-9_-]+", "", filename)

    def __str__(self):
        text = (
            "ProjectDTO. Name: {0}, filename: {1}, project web: {2}, "
            "disabled {3}, softcatala {4}, quality report {5}"
        )
        return text.format(
            self.name,
            self.filename,
            self.projectweb,
            self.disabled,
            self.softcatala,
            self.quality_report,
        )


class FileSetDTO(object):
    def __init__(self):
        self.name = ""
        self.url = ""
        self.type = ""
        self.target = ""
        self.pattern = ""
        self.duplicates = ""
        self.conversor_setup = None
        self.po_preprocessing = ""
        self.retrieval_pattern = ""

    def __str__(self):
        text = (
            "FileSetDTO. Name: {0}, url: {1}, type: {2}, target: {3},"
            "pattern: {4}, duplicates: {5}, po_preprocessing {6}, "
            "retrieval_pattern {7}"
        )
        return text.format(
            self.name,
            self.url,
            self.type,
            self.target,
            self.pattern,
            self.duplicates,
            self.po_preprocessing,
            self.retrieval_pattern,
        )


class ConversorSetupDTO(object):
    def __init__(self):
        self.type = ""
        self.verb = ""
        self.command = ""

    def __str__(self):
        text = "ConversorSetupDTO. Type: {0}, verb: {1}, command: {2}"
        return text.format(self.type, self.verb, self.command)


class JsonBackend(object):
    def __init__(self, directory, validation=False):
        self.directory = directory
        self.validation = validation
        self.projects = []

    def _process_conversor(self, fileset, conversor_values):
        conversor_setup = ConversorSetupDTO()

        for properties_attr, properties_value in conversor_values.items():
            if properties_attr == "type":
                conversor_setup.type = properties_value
            elif properties_attr == "verb":
                conversor_setup.verb = properties_value
            elif properties_attr == "command":
                conversor_setup.command = properties_value

        fileset.conversor_setup = conversor_setup

    def _process_fileset(self, project, project_value):
        for fileset_attr, fileset_value in project_value.items():
            fileset = FileSetDTO()
            project.filesets.append(fileset)
            fileset.name = fileset_attr

            self._process_file_set_attributes(fileset, fileset_value)

    def _process_file_set_attributes(self, fileset, fileset_value):
        for fileset_properties_attr, fileset_properties_value in fileset_value.items():
            if fileset_properties_attr == "name":
                fileset.name = fileset_properties_value
            elif fileset_properties_attr == "url":
                fileset.url = fileset_properties_value
            elif fileset_properties_attr == "type":
                fileset.type = fileset_properties_value
            elif fileset_properties_attr == "target":
                fileset.target = fileset_properties_value
            elif fileset_properties_attr == "pattern":
                fileset.pattern = fileset_properties_value
            elif fileset_properties_attr == "duplicates":
                fileset.duplicates = fileset_properties_value
            elif fileset_properties_attr == "conversor_setup":
                self._process_conversor(fileset, fileset_value["conversor_setup"])
            elif fileset_properties_attr == "po_preprocessing":
                fileset.po_preprocessing = fileset_properties_value
            elif fileset_properties_attr == "retrieval_pattern":
                fileset.retrieval_pattern = fileset_properties_value
            else:
                msg = "Field '{0}' not recognized"
                logging.error(msg.format(fileset_properties_attr))
                if self.validation:
                    raise Exception(msg)

    def load(self):
        findFiles = FindFiles()

        for filename in findFiles.find_recursive(self.directory, "*.json"):
            self._load_file(filename)

    def _load_file(self, filename):
        try:
            with open(filename) as json_data:
                data = json.load(json_data, object_pairs_hook=OrderedDict)

                # Parse projects
                project = ProjectDTO(data["project"])
                for attribute, value in data.items():
                    if attribute in (
                        "filename",
                        "projectweb",
                        "softcatala",
                        "disabled",
                        "downloadable",
                        "selectable",
                        "license",
                        "quality_report",
                    ):
                        setattr(project, attribute, data[attribute])

                    if "fileset" in attribute:
                        self._process_fileset(project, data["fileset"])

                if project.disabled is False:
                    self.projects.append(project)
        except Exception as detail:
            msg = "JsonBackend._load_file. Cannot load {0}. Error: {1}".format(
                filename, detail
            )
            logging.error(msg)
            if self.validation:
                raise
