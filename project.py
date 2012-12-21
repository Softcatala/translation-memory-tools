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

class Project:

	filesets = list()

	def __init__(self, filename):
		self.filename = filename

		if (os.path.isfile(filename)):
			os.system("rm " + filename)

	def GetFilename(self):
		return self.filename;

	def Add(self, fileset):
		fileset.SetTMFile(self.filename)
		self.filesets.append(fileset)

	def Do(self):
		for fileset in self.filesets:
			fileset.Do()



