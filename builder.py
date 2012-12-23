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

import logging

from fileset import *
from project import *
from projects import *

projects = Projects("tm.po")
reRecreateTM = True


def CreateProject(filename):
	project = Project(filename)
	project.SetRecreateTM(reRecreateTM)
	projects.Add(project)
	return project
	

def ubuntu():

	# https://translations.launchpad.net/ubuntu/quantal/+lang/ca

	project = CreateProject("ubuntu-tm.po")

	project.Add(BazaarFileSet('ubuntu-software-center', 'bzr cat lp:ubuntu/software-center/po/ca.po', 'ca.po'))
	project.Add(BazaarFileSet('ubuntu-update-manager', 'bzr cat lp:ubuntu/update-manager/po/ca.po', 'ca.po'))
	project.Do()

def gnome():

	project = CreateProject("gnome-tm.po")

	project.Add(CompressedFileSet('gnome-ui', 'http://l10n.gnome.org/languages/ca/gnome-3-8/ui.tar.gz', 'gnome-ui.tar.gz'))
	project.Add(CompressedFileSet('gnome-office', 'http://l10n.gnome.org/languages/ca/gnome-office/ui.tar.gz', 'gnome-office.tar.gz'))
	project.Add(CompressedFileSet('gnome-extras', 'http://l10n.gnome.org/languages/ca/gnome-extras/ui.tar.gz', 'gnome-extras.tar.gz'))
	project.Add(CompressedFileSet('gnome-external', 'http://l10n.gnome.org/languages/ca/external-deps/ui.tar.gz', 'gnome-external.tar.gz'))
	project.Add(CompressedFileSet('gnome-infrastructure', 'http://l10n.gnome.org/languages/ca/gnome-infrastructure/ui.tar.gz', 'gnome-infrastructure.tar.gz'))
	project.Add(CompressedFileSet('gimp', 'http://l10n.gnome.org/languages/ca/gnome-gimp/ui.tar.gz', 'gimp.tar.gz'))
	project.Add(BazaarFileSet('gnome-inkscape', 'bzr cat lp:inkscape/po/ca.po', 'ca.po'))
	project.Add(CompressedFileSet('freedesktop', 'http://l10n.gnome.org/languages/ca/freedesktop-org/ui.tar.gz', 'freesktop.tar.gz'))
	project.Add(CompressedFileSet('olpc', 'http://l10n.gnome.org/languages/ca/olpc/ui.tar.gz', 'olpc.tar.gz'))
	project.Do()

def mozilla():

	project = CreateProject("mozilla-tm.po")
	mozillaSet = CompressedFileSet('mozilla', 'http://pootle.softcatala.org/ca/mozilla/export/zip', 'mozilla.zip')
	mozillaSet.AddExcluded('region.properties.po')
	project.Add(mozillaSet)

	project.Add(CompressedFileSet('mozilla-gaia', 'http://pootle.softcatala.org/ca/gaia/export/zip', 'gaia.zip'))
	project.Add(CompressedFileSet('mozilla-addons', 'http://localize.mozilla.org/ca/amo/export/zip', 'add-ons.zip'))
	project.Do()

def libreoffice():

	project = CreateProject("libreoffice-tm.po")
	project.Add(CompressedFileSet('LibreOffice.org ajuda', 'https://translations.documentfoundation.org/ca/libo_help/export/zip', 'libreoffice-help.zip'))
	project.Add(CompressedFileSet('LibreOffice.org UI', 'https://translations.documentfoundation.org/ca/libo_ui/export/zip', 'libreoffice-ui.zip'))
	project.Add(CompressedFileSet('LibreOffice.org lloc web', 'https://translations.documentfoundation.org/ca/website/export/zip', 'website.zip'))
	project.Add(CompressedFileSet('LibreOffice.org ask bot', 'https://translations.documentfoundation.org/ca/askbot/export/zip', 'askbot.zip'))
	project.Do()

def abiword():

	project = CreateProject("abiword-tm.po")
	project.Add(CompressedFileSet('abiword', 'http://www.abisource.com/dev/strings/dev/ca-ES.po', 'abiword-ca.po'))
	project.Do()

def fedora():

	project = CreateProject("fedora-tm.po")
	project.Add(TransifexFileSet('fedora', 'https://fedora.transifex.net/projects/p/fedora/r/fedora-upstream-projects/', ''))
	project.Do()

def recull():

	project = CreateProject("recull-tm.po")
	project.Add(LocalFileSet('recull', 'recull/recull.po', 'recull.po'))
	project.Do()

def mandriva():

	project = CreateProject("mandriva-tm.po")
	project.Add(LocalDirFileSet('mandriva', 'mandriva-po/*.po', ''))
	project.Do()

def initLogging():

	logfile = "builder.log"

	if (os.path.isfile(logfile)):
			os.system("rm " + logfile)

	logging.basicConfig(filename=logfile,level=logging.DEBUG)
	logger = logging.getLogger('')
	ch = logging.StreamHandler()
	logger.addHandler(ch)

def main():

	print "Translation memory builder version 0.1"

	start_time = time.time()

	initLogging()

	recull()
	abiword()
	fedora()
	mozilla()
	gnome()
	libreoffice()
	ubuntu()
	mandriva()

	projects.Do()

	print "Execution time:", time.time() - start_time, "seconds"

if __name__ == "__main__":
    main()


