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
import sys
import logging

from fileset import *

class Project:

	def __init__(self, name, filename):
		self.recreateTM = True
		self.addSource = True
		self.filename = filename
		self.filesets = list()
		self.name = name

	def GetFilename(self):
		return self.filename;

	def SetRecreateTM(self, recreateTM):
		self.recreateTM = recreateTM

	def SetAddSource(self, addSource):
		self.addSource = addSource

	def DeletePOFile(self):
		if (os.path.isfile(self.filename)):
			os.system("rm " + self.filename)

	def Add(self, fileset):
		fileset.SetTMFile(self.filename)
		self.filesets.append(fileset)

	def Do(self):
		try:

			if (self.recreateTM == False and os.path.isfile(self.filename)):
				return
			
			self.DeletePOFile()

			for fileset in self.filesets:
				fileset.SetAddSource(self.addSource)
				fileset.Do()

		except Exception as detail:
			logging.error("Project.Do. Cannot complete " + self.filename)
			logging.error(detail)
			self.DeletePOFile()

	def Statistics(self):
		
		poFile = polib.pofile(self.filename)
		s = self.name + " project. " + str(len(poFile.translated_entries())) + " translated strings"
		print s
		logging.info(s)


