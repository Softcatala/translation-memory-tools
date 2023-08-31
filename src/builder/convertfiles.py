# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import shutil

from .converttmx import ConvertTmx
from .findfiles import FindFiles
from .convertini import ConvertIni
from enum import Enum


class ConversorID(str, Enum):
    Ts = "ts"
    Strings = "strings"
    Php = "php"
    Android = "android"
    Properties = "properties"
    Json = "json"
    Csv = "cvs"
    Apple = "apple"


class ConvertFiles:
    def __init__(self, convert_dir, conversor_setup):
        self.convert_dir = convert_dir
        self.findFiles = None
        self.conversor_setup = conversor_setup

    def convert(self):
        self.findFiles = FindFiles()
        self._uncompress_files()
        self._convert_tmx_files_to_po()
        self._convert_ts_files_to_po()
        self._convert_strings_files_to_po()
        self._convert_ini_files_to_po()
        self._convert_php_resources_files_to_po()
        self._convert_android_resources_files_to_po()
        self._convert_apple_resources_files_to_po()
        self._convert_properties_files_to_po()
        self._convert_json_files_to_po()
        self._convert_yml_files_to_po()
        self._convert_csv_files_to_po()
        self._convert_xliff_file_to_po()

    def _add_conversor_setup_to_cmd(self, cmd, conversor_id=None):
        if (
            self.conversor_setup
            and conversor_id
            and conversor_id.lower() == self.conversor_setup.type
        ):
            if (
                self.conversor_setup.type == conversor_id
                and self.conversor_setup.verb == "add"
            ):
                cmd += self.conversor_setup.command
                logging.info(
                    f"Adding to conversor '{conversor_id}' parameter '{self.conversor_setup.command}'"
                )

        return cmd

    def _convert_ts_files_to_po(self):
        for tsfile in self.findFiles.find_recursive(self.convert_dir, "*.ts"):
            fileName, fileExtension = os.path.splitext(tsfile)
            logging.info("convert ts file: {0}".format(tsfile))
            cmd = self._add_conversor_setup_to_cmd(
                "ts2po {0} -o {1}.po".format(tsfile, fileName), ConversorID.Ts
            )
            os.system(cmd)

    def _convert_strings_files_to_po(self):
        for tsfile in self.findFiles.find_recursive(self.convert_dir, "ca.strings"):
            dirName = os.path.dirname(tsfile)
            logging.info("convert strings file: {0}".format(dirName))
            filename = "{0}/strings-ca.po".format(dirName)
            # Allow process files with duplicated entries
            cmd = (
                "prop2po -t {0}/en.strings {0}/ca.strings "
                "--personality strings --duplicates merge -o {1}"
            )
            cmd = self._add_conversor_setup_to_cmd(
                cmd.format(dirName, filename), ConversorID.Strings
            )
            os.system(cmd)

    def _uncompress_files(self):
        for zipfile in self.findFiles.find_recursive(self.convert_dir, "*.zip"):
            # Some projects have files with passwords that we do not know,
            # we pass an 'unknown' password to prevent been prompted for it
            cmd = "unzip -p unknown -t {0} > /dev/null ".format(zipfile)
            os.system(cmd)

    def _convert_tmx_files_to_po(self):
        for tmxfile in self.findFiles.find_recursive(self.convert_dir, "*.tmx"):
            fileName, fileExtension = os.path.splitext(tmxfile)
            tmx = ConvertTmx(tmxfile, fileName + ".po")
            tmx.convert()
            logging.info("convert tmx file: {0}".format(tmxfile))

    def _convert_csv_files_to_po(self):
        for csvfile in self.findFiles.find_recursive(self.convert_dir, "ca.csv"):
            dirName = os.path.dirname(csvfile)
            pofile = dirName + "/ca.po"
            cmd = "csv2po -i {0} -o {1}".format(csvfile, pofile)
            cmd = self._add_conversor_setup_to_cmd(cmd, ConversorID.Csv)
            os.system(cmd)
            logging.info("convert csv file: {0}".format(csvfile))

    def _convert_properties_files_to_po(self):
        en_file = "en.properties"
        files = self.findFiles.find_recursive(self.convert_dir, "ca.properties")
        if len(files) == 0:
            files = self.findFiles.find_recursive(self.convert_dir, "ca_ES.properties")

        if len(files) == 0:
            files = self.findFiles.find_recursive(
                self.convert_dir, "dictionary_ca.properties"
            )
            if len(files) > 0:
                en_file = "dictionary.properties"

        for propfile in files:
            dirName = os.path.dirname(propfile)
            prop_filename = os.path.basename(propfile)
            logging.info("convert properties file: {0}".format(dirName))
            po_filename = "{0}/properties-ca.po".format(dirName)
            # Allow process files with duplicated entries
            cmd = (
                f"prop2po -t {dirName}/{en_file} {dirName}/{prop_filename} "
                f"--personality java --duplicates merge -o {po_filename}"
            )

            cmd = self._add_conversor_setup_to_cmd(cmd, ConversorID.Properties)
            os.system(cmd)

    def _convert_ini_files_to_po(self):
        for inifile in self.findFiles.find_recursive(self.convert_dir, "*.ini"):
            dirName = os.path.dirname(inifile)
            filename = os.path.basename(inifile)

            trg = None
            for filename in ["ca.ini", "CA.ini", "ca_ES.ini", "ca-ES.ini"]:
                fullName = "{0}/{1}".format(dirName, filename)
                if filename in inifile:
                    trg = fullName
                    break

            src = None
            for filename in ["en.ini", "EN.ini", "en_GB.ini", "en-US.ini"]:
                fullName = "{0}/{1}".format(dirName, filename)
                if os.path.isfile(fullName):
                    src = fullName
                    break

            if src is None or trg is None:
                continue

            logging.info("convert ini file: {0}".format(inifile))
            filename = "{0}/strings-ca.po".format(dirName)
            ConvertIni(src, trg, filename).convert()

    def _convert_php_resources_files_to_po(self):
        if len(self.findFiles.find_recursive(self.convert_dir, "*.php")) == 0:
            return

        logging.info("convert php directory: {0}".format(self.convert_dir))
        # Name arbitrary choosen (not sepecific to an expected dir structure)
        OUT_DIRNAME = "po-files"
        cmd = "cd {0} && php2po -t en -i ca " "-o {1}".format(
            self.convert_dir, OUT_DIRNAME
        )
        cmd = self._add_conversor_setup_to_cmd(cmd, ConversorID.Php)
        os.system(cmd)

    def _convert_android_file(self, src_file, tgt_file, id):
        output_file = os.path.join(self.convert_dir, f"ca-{id}.po")
        cmd = f"android2po -t {src_file} -i {tgt_file} -o {output_file}"
        cmd = self._add_conversor_setup_to_cmd(cmd, ConversorID.Android)
        os.system(cmd)

    # Some times Android resources are found in values/ and values-ca/ subdirectories
    # Other times, just in the same subdirectory (en.xml and ca.xml)
    def _convert_android_resources_files_to_po(self):
        filenames = self.findFiles.find_recursive(self.convert_dir, "*.xml")
        if len(filenames) == 0:
            return

        id = 0
        dirs = set()
        subdirs = set()
        for filename in filenames:
            dir = os.path.dirname(filename)
            if dir in dirs:
                continue

            dirs.add(dir)
            src = os.path.join(dir, "en.xml")
            tgt = os.path.join(dir, "ca.xml")

            if os.path.exists(src) and os.path.exists(tgt):
                self._convert_android_file(src, tgt, id)
                id += 1

            if dir == self.convert_dir:
                continue

            # Remove subdir where file was found a/b/c/strings.xml becomes a/b/values/strings.xml
            dir = os.path.dirname(dir)
            if len(dir) > 0:
                if dir in subdirs:
                    continue

                subdirs.add(dir)

                for src, tgt in zip(
                    ["values/strings.xml", "values/strings.xml"],
                    ["values-ca/strings.xml", "values-ca-rES/strings.xml"],
                ):
                    src = os.path.join(dir, src)
                    tgt = os.path.join(dir, tgt)

                    if os.path.exists(src) and os.path.exists(tgt):
                        self._convert_android_file(src, tgt, id)
                        id += 1

        logging.info("convert Android directory: {0}".format(self.convert_dir))

    def _convert_json_file_to_po(self, jsonfile, source, target):
        dirName = os.path.dirname(jsonfile)
        logging.info("convert json file: {0}".format(dirName))
        filename = "{0}/json-ca.po".format(dirName)
        cmd = "json2po -t {0}/{2} -i {0}/{3} " "-o {1}".format(
            dirName, filename, source, target
        )
        cmd = self._add_conversor_setup_to_cmd(cmd, ConversorID.Json)
        os.system(cmd)

    def _convert_json_files_to_po(self):
        # Used for Privacy Badger
        for jsonfile in self.findFiles.find_recursive(
            self.convert_dir, "messages.json"
        ):
            if "/ca/" not in jsonfile:
                continue

            self._convert_json_file_to_po(
                jsonfile, "../en_US/messages.json", "../ca/messages.json"
            )

        for jsonfile in self.findFiles.find_recursive(self.convert_dir, "ca.json"):
            self._convert_json_file_to_po(jsonfile, "en.json", "ca.json")

        for jsonfile in self.findFiles.find_recursive(self.convert_dir, "ca.i18n.json"):
            self._convert_json_file_to_po(jsonfile, "en.i18n.json", "ca.i18n.json")

        for jsonfile in self.findFiles.find_recursive(self.convert_dir, "ca-CA.json"):
            self._convert_json_file_to_po(jsonfile, "en-US.json", "ca-CA.json")

        for jsonfile in self.findFiles.find_recursive(self.convert_dir, "main-ca.json"):
            self._convert_json_file_to_po(jsonfile, "main.json", "main-ca.json")

    def _convert_yml_files_to_po(self):
        EXPECTED_SRC = "en.yml"
        EXPECTED_TRG = "ca.yml"

        for trgfile in self.findFiles.find_recursive(self.convert_dir, "*ca.yml"):
            srcfile = trgfile.replace("ca.yml", "en.yml")

            if os.path.isfile(srcfile) is False:
                continue

            dirName = os.path.dirname(srcfile)
            src_base = os.path.basename(srcfile)
            if src_base != EXPECTED_SRC:
                new = os.path.join(dirName, EXPECTED_SRC)
                shutil.copyfile(srcfile, new)

            trg_base = os.path.basename(trgfile)
            if trg_base != EXPECTED_TRG:
                new = os.path.join(dirName, EXPECTED_TRG)
                shutil.copyfile(trgfile, new)

            logging.info("convert yml file: {0}".format(dirName))
            cmd = "i18n-translate convert --locale_dir {0} -f yml -l ca -t po -d en".format(
                dirName
            )
            cmd = self._add_conversor_setup_to_cmd(cmd)
            os.system(cmd)

    def _convert_xliff_file_to_po(self):
        for xlfile in self.findFiles.find_recursive(self.convert_dir, "*.xliff"):
            fileName, fileExtension = os.path.splitext(xlfile)
            pofile = xlfile.replace(".xliff", ".po")
            cmd = f'xliff2po -i "{xlfile}" -o "{pofile}" --duplicates=merge'
            cmd = self._add_conversor_setup_to_cmd(cmd)
            os.system(cmd)

    def _convert_apple_file(self, src_file, tgt_file, id):
        output_file = os.path.join(self.convert_dir, f"ca-apple-{id}.po")
        cmd = f"prop2po -t {src_file} -i {tgt_file} -o {output_file} --personality strings --duplicates merge"
        cmd = self._add_conversor_setup_to_cmd(cmd, ConversorID.Apple)
        if "--encoding" not in cmd:
            cmd += " --encoding utf-8"

        os.system(cmd)

    def _convert_apple_resources_files_to_po(self):
        filenames = self.findFiles.find_recursive(
            self.convert_dir, "Localizable.strings"
        )
        if len(filenames) == 0:
            return

        id = 0
        dirs = set()
        subdirs = set()
        for filename in filenames:
            dir = os.path.dirname(filename)
            if dir in dirs:
                continue

            dirs.add(dir)
            if dir == self.convert_dir:
                continue

            # Remove subdir where file was found a/b/c/Localizable.strings becomes en.lproj/Localizable.strings
            dir = os.path.dirname(dir)
            if len(dir) > 0 and dir not in subdirs:
                subdirs.add(dir)
                src = os.path.join(dir, "en.lproj/Localizable.strings")
                tgt = os.path.join(dir, "ca.lproj/Localizable.strings")

                if os.path.exists(src) and os.path.exists(tgt):
                    self._convert_apple_file(src, tgt, id)
                    id += 1
                else:
                    src = os.path.join(dir, "Base.lproj/Localizable.strings")
                    tgt = os.path.join(dir, "ca.lproj/Localizable.strings")
                    if os.path.exists(src) and os.path.exists(tgt):
                        self._convert_apple_file(src, tgt, id)
                        id += 1

        logging.info("convert Apple directory: {0}".format(self.convert_dir))
