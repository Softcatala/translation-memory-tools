#!/usr/bin/env python
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

from downloadfile import DownloadFile
from findfiles import FindFiles
from shtuil import rmtree
from shutil import move

import logging
import os
import polib


logfile = 'apply-tm.log'
temp_dir = './tmp'
output_dir = './gnome'

GNOME_VERSION = '3-8'
GNOME_URL = 'https://l10n.gnome.org/languages/ca'
GNOME_SETS = (
    '{0}/gnome-{1}/ui.tar.gz'.format(GNOME_URL, GNOME_VERSION),
    '{0}/gnome-extras/ui.tar.gz'.format(GNOME_URL),
    '{0}/gnome-office/ui.tar.gz'.format(GNOME_URL),
    '{0}/external-deps/ui.tar.gz'.format(GNOME_URL),
    '{0}/gnome-infrastructure/ui.tar.gz'.format(GNOME_URL),
    '{0}/gnome-gimp/ui.tar.gz'.format(GNOME_URL),
)


def process(url):

    newtranslated = 0
    filename = 'translations.tar.gz'

    download = DownloadFile()
    download.GetFile(url, filename)
    logging.info('Downloaded {0}'.format(url))

    # Uncompress
    os.system('tar -xvf {0} -C {1}'.format(filename, temp_dir))

    # Apply tm
    findFiles = FindFiles()

    for filename in findFiles.Find(temp_dir, '*.po*'):

        try:

            tmfilename = '{0}/tm-{1}'.format(
                os.path.dirname(filename),
                os.path.basename(filename)
            )
            command = 'msgmerge -N {0} {0} -C latest-nosource/tm.po ' \
                '> {1} 2> /dev/null'.format(filename, tmfilename)
            os.system(command)
            logging.info(command)

            infile = polib.pofile(filename)
            tmfile = polib.pofile(tmfilename)

            intranslated = len(infile.translated_entries())
            tmtranslated = len(tmfile.translated_entries())

            if tmtranslated > intranslated + 20:
                new = tmtranslated - intranslated
                print '{0} original: {1} , tm: {2} new translated {3}'.format(
                    filename,
                    intranslated,
                    tmtranslated,
                    new
                )
                dfilename = '{0}/diff-{1}'.format(
                    os.path.dirname(filename),
                    os.path.basename(filename)
                )
                command = 'diff -u {0} {1} > {2}'.format(
                    filename,
                    tmfilename,
                    dfilename
                )
                os.system(command)
                logging.info(command)
                newtranslated += new
                move(filename, output_dir)
                move(tmfilename, output_dir)
                move(dfilename, output_dir)
            else:
                os.remove(filename)
                os.remove(tmfilename)

        except Exception as detail:
            msg = 'Cannot complete {0}'.format(filename)
            print msg
            logging.error(msg)
            logging.error(detail)

    return newtranslated


def initLogging():
    if os.path.isfile(logfile):
        os.remove(logfile)

    logging.basicConfig(filename=logfile, level=logging.DEBUG)


if __name__ == '__main__':
    initLogging()

    rmtree(temp_dir)
    os.makedirs(temp_dir)
    rmtree(output_dir)
    os.makedirs(output_dir)

    newtranslated = 0
    for gnome_set in GNOME_SETS:
        newtranslated += process(gnome_set)

    print 'Total new strings {0}'.format(newtranslated)
