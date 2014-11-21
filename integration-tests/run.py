#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import sys
sys.path.append('../src/')

from optparse import OptionParser
from checkdownloads import CheckDownloads
from checksearch import CheckSearch
from crawler import Crawler
import ConfigParser
from collections import OrderedDict

site_url = None


def read_parameters():
    global site_url
    SECTION = "default"

    parser = OptionParser()
    config = ConfigParser.ConfigParser()
    config.read("environments.conf")
    environments = OrderedDict()

    for option in config.options(SECTION):
        environments[option] = config.get(SECTION, option)

    opt_environments = ', '.join(environments.keys())
    default = next(reversed(environments))
    parser.add_option("-e", "--environment", dest="environment", 
                      default=default, type="choice", choices=environments.keys(),
                      help="set default environment to: " + opt_environments)

    (options, args) = parser.parse_args()
    site_url = environments.get(options.environment, None)


if __name__ == '__main__':
    read_parameters()
    print("Integration tests for: " + site_url)
    print("Use --help for assistance")

    search = CheckSearch(site_url)
    if not search.check():
        sys.exit(1)

    crawler = Crawler(site_url + "memories.html")
    crawler.run()
    
    downloads = CheckDownloads(crawler.get_all_links())
    downloads.check()

    if downloads.errors > 0:
        print('Total download errors {0}'.format(downloads.errors))
        sys.exit(1)

    sys.exit(0)
