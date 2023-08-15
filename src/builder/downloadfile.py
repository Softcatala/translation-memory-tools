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

import logging
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError


class DownloadFile(object):
    def urlopen_with_retry(self, url):
        NTRIES = 3
        NOT_FOUND = 404
        TIMEOUT = 15

        timeout = TIMEOUT
        for ntry in range(NTRIES):
            try:
                req = Request(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64;) Gecko Firefox"
                    },
                )
                return urlopen(req, timeout=timeout)
            except HTTPError as e:
                logging.error(
                    f"HTTPError on urlopen_with_retry. URL: '{url}', error: '{e}'"
                )
                if e.code == NOT_FOUND:
                    return
            # May be server load that needs more time to compute the request
            except TimeoutError as e:
                if ntry + 1 == NTRIES:
                    logging.error(
                        f"Time out error on urlopen_with_retry. URL: '{url}', error: '{e}'"
                    )
                timeout = timeout * 4
            except Exception as e:
                print(type(e))
                logging.error(
                    f"Error on urlopen_with_retry. URL: '{url}', error: '{e}'"
                )

    def _remove_incomplete_file(self, filename):
        if os.path.exists(filename):
            os.remove(filename)

    def get_file(self, url, filename):
        try:
            msg = "Downloading file '{0}' to {1}".format(url, filename)
            logging.info(msg)

            infile = self.urlopen_with_retry(url)
            output = open(filename, "wb")
            output.write(infile.read())
            output.close()
        except Exception:
            msg = "Error downloading file '{0}' to {1}".format(url, filename)
            logging.error(msg)
            self._remove_incomplete_file(filename)
