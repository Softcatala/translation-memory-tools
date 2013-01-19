#!/usr/bin/env python2
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
from optparse import OptionParser
from fileset import *
from project import *
from projects import *
from jsonbackend import *

projects = Projects("tm.po")
reRecreateTM = True
addSource = True


def CreateProject(filename):
	project = Project(filename)
	project.SetRecreateTM(reRecreateTM)
	project.SetAddSource(addSource)
	projects.Add(project)
	return project
	
def initLogging():

	logfile = "builder.log"

	if (os.path.isfile(logfile)):
			os.system("rm " + logfile)

	logging.basicConfig(filename=logfile,level=logging.DEBUG)
#	logger = logging.getLogger('')
#	ch = logging.StreamHandler()
#	logger.addHandler(ch)

def readParameters():

	parser = OptionParser()
	parser.add_option("-n", "--no-source",
		              action="store_false", dest="addSource", default=True,
		              help="Do not include the source for the translation segment")

	(options, args) = parser.parse_args()

	global addSource

	addSource = options.addSource

def processProjects():

	json = JsonBackend('projects.json')
	json.load()

	for project_dto in json.projects:

		project = CreateProject(project_dto.filename)
		logging.info(project_dto)
		
		for fileset in project_dto.filesets:
			logging.info(fileset)
			if (fileset.type == 'local-po'):
				project.Add(LocalFileSet(fileset.name, fileset.url, fileset.target))
			elif (fileset.type == 'compressed'):
				project.Add(CompressedFileSet(fileset.name, fileset.url, fileset.target))
			elif (fileset.type ==  'bazaar'):
				project.Add(BazaarFileSet(fileset.name, fileset.url, fileset.target))
			elif (fileset.type == 'transifex'):
				project.Add(TransifexFileSet(fileset.name, fileset.url, fileset.target))
			elif (fileset.type == 'local-dir'):
				project.Add(LocalDirFileSet(fileset.name, fileset.url, fileset.target))

		project.Do()

	projects.Do()

def main():

	print "Translation memory builder version 0.1"

	start_time = time.time()

	initLogging()
	readParameters()
	processProjects()

	print "Execution time:", time.time() - start_time, "seconds"

if __name__ == "__main__":
    main()


