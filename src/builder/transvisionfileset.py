# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import os
import polib

from fileset import FileSet
from downloadfile import DownloadFile
import xml.etree.ElementTree

class TransvisionFileSet(FileSet):
    """
        For Mozilla FR Transvision localization tool
    """

    def _download_files(self, tmxfile):
        # Download file selection
        download = DownloadFile()
        download.get_file(self.url, os.path.join(self.url, 'tempfile'))

        # Download translations
        download = DownloadFile()
        fullpath = os.path.join(self.temp_dir, tmxfile)
        download.get_file('https://transvision.mozfr.org/download/' + tmxfile, fullpath)
        return fullpath

    def _create_po(self):
        pofile = polib.POFile()
        pofile.metadata = {
            'Project-Id-Version': '1.0',
            'Report-Msgid-Bugs-To': 'info@mozilla.org',
            'POT-Creation-Date': '2016-01-01 14:00+0100',
            'PO-Revision-Date': '2016-01-01 14:00+0100',
            'Last-Translator': 'info@mozilla.org',
            'Language-Team': 'Catalan <mozilla@llistes.softcatala.org>',
            'MIME-Version': '1.0',
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
            'Plural-Forms': 'nplurals=2; plural=n != 1;',
        }
        return pofile

    def _tmx_to_po(self, xmlfile, pofile):

        po = self._create_po()
        msgids = set()
        e = xml.etree.ElementTree.parse(xmlfile).getroot()
        e = e.find('body')
        for tu in e.findall('tu'):
            source = u''
            target = u''
            context = None
            comment = unicode(tu.get('tuid'))
            for tuv in tu.findall('tuv'):
                # attribute xml:lang
                lang = tuv.get('{http://www.w3.org/XML/1998/namespace}lang')
                seg = tuv.find('seg')
                if lang == 'en-US':
                    source = unicode(seg.text)
                elif lang == 'ca':
                    target = unicode(seg.text)

            if source in msgids:
                context = comment
            else:
                msgids.add(source)

            entry = polib.POEntry(msgid=source, msgstr=target, comment=comment, msgctxt=context)
            po.append(entry)

        po.save(pofile)
        print "PO saved entries to: " + pofile

    def do(self):
        tmxfile = 'mozilla_en-US_ca.tmx'
        downloaded_tmx = self._download_files(tmxfile)
        fullpath = os.path.join(self.temp_dir, 'mozilla.po')
        self._tmx_to_po(downloaded_tmx, fullpath)
        self.build()
