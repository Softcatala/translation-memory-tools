#!/usr/bin/python2
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


import os

from fileset import *

class Projects:

	tmfile = "tm.po"
	projects = list()

	def __init__(self, filename):
		self.filename = filename

		if (os.path.isfile(filename)):
			os.system("rm " + filename)

	def Add(self, project):
		self.projects.append(project)

	def Do(self):
		first = False

		for project in self.projects:
			os.system("msgcat -tutf-8 --use-first -o " + self.tmfile + " " + project.GetFilename())

		os.system("msgfmt -c --statistics " + self.tmfile)



