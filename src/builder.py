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
addSource = True
	
def initLogging():

	logfile = "builder.log"

	if (os.path.isfile(logfile)):
		os.system("rm " + logfile)

	logging.basicConfig(filename=logfile,level=logging.DEBUG)
	logger = logging.getLogger('')
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	logger.addHandler(console)

def readParameters():

	parser = OptionParser()
	parser.add_option("-n", "--no-source",
			action="store_false", dest="addSource", default=True,
			help="Do not include the source for the translation segment")

	parser.add_option("-p", "--projects",
			action="store", type="string", dest="projectNames",
			help="To restrict the processing of projects to comma sparated given list e.g.: (fedora,ubuntu)")

	(options, args) = parser.parse_args()

	global addSource
	global projectsNames
 
	addSource = options.addSource

	if (options.projectNames is not None):
		projectsNames = options.projectNames.split(",")
	else:
		projectsNames = None

def processProjects():

	global addSource

	json = JsonBackend('projects.json')
	json.load()

	for project_dto in json.projects:

		if (projectsNames is not None):
			found = False
			for projectName in projectsNames:
				if projectName.lower().strip() == project_dto.name.lower().strip():
					found = True

			if found == False:
				continue;

		projects.AddProject(project_dto, addSource)

	projects.Do()

def main():

	print "Translation memory builder version 0.1"
	print "Use --help for assistance"

	start_time = time.time()

	initLogging()
	readParameters()
	processProjects()
	projects.ToTmx()
	projects.Statistics()

	s= "Execution time: " + str(time.time() - start_time) + " seconds"
	logging.info(s)

if __name__ == "__main__":
    main()


