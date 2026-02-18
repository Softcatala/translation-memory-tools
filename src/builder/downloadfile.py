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
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError


class DownloadFile(object):
    def urlopen_with_retry(self, url, headers=None):
        NTRIES = 3
        NOT_FOUND = 404
        TOO_MANY_REQUESTS = 429
        TIMEOUT = 15
        DEFAULT_BACKOFF = 30
        timeout = TIMEOUT
        for ntry in range(NTRIES):
            try:
                if not headers:
                    if "hosted.weblate.org" in url:
                        headers = {}
                    else:
                        headers = {
                            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64;) Gecko Firefox"
                        }
                req = Request(
                    url,
                    headers=headers,
                )
                return urlopen(req, timeout=timeout)
            except HTTPError as e:
                logging.error(
                    f"HTTPError on urlopen_with_retry. URL: '{url}', error: '{e}'"
                )
                if e.code == NOT_FOUND:
                    return
                if e.code == TOO_MANY_REQUESTS:
                    if ntry + 1 == NTRIES:
                        logging.error(
                            f"Too many requests on urlopen_with_retry. URL: '{url}', giving up after {NTRIES} tries."
                        )
                        return
                    retry_after = int(e.headers.get("Retry-After", DEFAULT_BACKOFF))
                    logging.warning(
                        f"Too many requests. Backing off for {retry_after}s before retry. URL: '{url}'"
                    )
                    time.sleep(retry_after)
            # May be server load that needs more time to compute the request
            except TimeoutError as e:
                if ntry + 1 == NTRIES:
                    logging.error(
                        f"Time out error on urlopen_with_retry. URL: '{url}', error: '{e}'"
                    )
                timeout = timeout * 4
            except Exception as e:
                logging.error(
                    f"Error on urlopen_with_retry. URL: '{url}', error: '{e}'"
                )

    def _remove_incomplete_file(self, filename):
        if os.path.exists(filename):
            os.remove(filename)

    def get_file(self, url, filename, headers=None):
        try:
            msg = "Downloading file '{0}' to {1}".format(url, filename)
            logging.info(msg)
            with self.urlopen_with_retry(url, headers) as infile:
                with open(filename, "wb") as output:
                    output.write(infile.read())
        except Exception:
            msg = "Error downloading file '{0}' to {1}".format(url, filename)
            logging.error(msg)
            self._remove_incomplete_file(filename)
