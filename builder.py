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


import urllib2
import os
import polib
import fnmatch
import time

class DownloadFile:

	def GetFile(self, url, filename):
		
		print 'Downloading file \'' + url + '\''

		infile = urllib2.urlopen(url)
		output = open(filename,'wb')
		output.write(infile.read())
		output.close()

class POFile:

	def AddCommentToAllEntries(self, filename, comment):

		bakfile = filename + ".bak"

		os.system("cp " + filename + " " + bakfile)

		input_po = polib.pofile(bakfile)

		for entry in input_po:
			entry.tcomment = comment
			
		input_po.save(filename)

class FindFiles:

	def Find(self, directory, pattern):
    		for root, dirs, files in os.walk(directory):
        		for basename in files:
				if fnmatch.fnmatch(basename, pattern):
                			filename = os.path.join(root, basename)
                			yield filename
	
class Project():

	temp_dir = "./tmp"

	def __init__(self, project, url, filename):
		self.project = project
		self.url = url
		self.filename = filename

	def AddComments(self):

		findFiles = FindFiles()

		for filename in findFiles.Find(self.temp_dir, '*.po'):
			relative = filename.replace(self.temp_dir, '')
			print 'Adding source reference to file:' + relative
			pofile = POFile()
			pofile.AddCommentToAllEntries(filename, "Translation source: " + relative +  " from project '" + self.project + "'")

	def Build(self):

		findFiles = FindFiles()

		for filename in findFiles.Find(self.temp_dir, '*.po'):

			print 'Adding file:' + filename + ' to translation memory'

			if (os.path.isfile("tm-project.po")):
				os.system("cp tm-project.po tm-project-previous.po")
				os.system("msgcat -tutf-8 --use-first -o tm-project.po tm-project-previous.po " + filename)
			else:
				os.system("cp " + filename + " tm-project.po")

		if (os.path.isfile("tm.po")):
			os.system("cp tm.po tm-previous.po")
			os.system("msgcat -tutf-8 --use-first -o tm.po tm-previous.po tm-project.po")
		else:
			os.system("cp tm-project.po tm.po")

	def Uncompress(self):

		os.system("rm -f -r " + self.temp_dir)

		if (self.filename.endswith('zip')):
			os.system("unzip " + self.filename + " -d " + self.temp_dir)
		elif (self.filename.endswith('tar.gz')):
			os.system("mkdir " + self.temp_dir)
			os.system("tar -xvf " + self.filename + " -C " + self.temp_dir)
		elif (self.filename.endswith('.po')):
			os.system("mkdir " + self.temp_dir)
			os.system("cp " + self.filename + " " + self.temp_dir + "/" + self.filename)
		else:
			print("Unsupport file extension for filename " + self.filename)



class CompressedFileProject(Project):

	def Do(self):

		# Download po files
		download = DownloadFile()
		download.GetFile(self.url, self.filename)

		self.Uncompress();

		self.AddComments()
		self.Build()

class BazaarProject(Project):

	def Do(self):

		os.system("rm -r -f tmp")
		os.system("mkdir tmp")
		os.system("cd tmp")
		os.system(self.url + " > ca.po")

		self.Uncompress();

		self.AddComments()
		self.Build()


def ubuntu():

	# https://translations.launchpad.net/ubuntu/quantal/+lang/ca

	project = BazaarProject('ubuntu-software-center', 'bzr cat lp:ubuntu/software-center/po/ca.po', 'ca.po')
	project.Do()	

	project = BazaarProject('ubuntu-update-manager', 'bzr cat lp:ubuntu/update-manager/po/ca.po', 'ca.po')
	project.Do()


def gnome():

	project = CompressedFileProject('gnome-ui', 'http://l10n.gnome.org/languages/ca/gnome-3-6/ui.tar.gz', 'gnome-ui.tar.gz')
	project.Do()

	project = CompressedFileProject('gnome-office', 'http://l10n.gnome.org/languages/ca/gnome-office/ui.tar.gz', 'gnome-office.tar.gz')
	project.Do()

	project = CompressedFileProject('gnome-extras', 'http://l10n.gnome.org/languages/ca/gnome-extras-stable/ui.tar.gz', 'gnome-extras.tar.gz')
	project.Do()

	project = CompressedFileProject('gnome-external', 'http://l10n.gnome.org/languages/ca/external-deps/ui.tar.gz', 'gnome-external.tar.gz')
	project.Do()

	project = CompressedFileProject('gnome-infrastructure', 'http://l10n.gnome.org/languages/ca/gnome-infrastructure/ui.tar.gz', 'gnome-infrastructure.tar.gz')
	project.Do()

	project = CompressedFileProject('freedesktop', 'http://l10n.gnome.org/languages/ca/freedesktop-org/ui.tar.gz', 'freesktop.tar.gz')
	project.Do()

	project = CompressedFileProject('gimp', 'http://l10n.gnome.org/languages/ca/gnome-gimp/ui.tar.gz', 'gimp.tar.gz')
	project.Do()

def mozilla():

	project = CompressedFileProject('mozilla', 'http://pootle.softcatala.org/ca/mozilla/export/zip', 'mozilla.zip')
	project.Do()

	project = CompressedFileProject('mozilla-gaia', 'http://pootle.softcatala.org/ca/gaia/export/zip', 'gaia.zip')
	project.Do()

	project = CompressedFileProject('mozilla-addons', 'http://localize.mozilla.org/ca/amo/export/zip', 'add-ons.zip')
	project.Do()

def libreoffice():

	project = CompressedFileProject('Terminology Help', 'https://translations.documentfoundation.org/ca/terminology/export/zip', 'terminology.zip');
	project.Do()

	project = CompressedFileProject('LibreOffice.org Help', 'http://translations.documentfoundation.org/ca/libo36x_help/export/zip', 'libreoffice-help.zip');
	project.Do()

	project = CompressedFileProject('LibreOffice.org UI', 'https://translations.documentfoundation.org/ca/libo36x_ui/export/zip', 'libreoffice-ui.zip');
	project.Do()

def main():

	print "Translation memory builder version 0.1"

	start_time = time.time()

	os.system("rm -f tm.po")
	os.system("rm -f tm-previous.po")
	os.system("rm -f tm-project.po")
	os.system("rm -f tm-project-previous.po")

	project = CompressedFileProject('recull', 'file:///home/jordi/dev/translation-memory-builder/recull.po', 'recull-downloaded.po')
	project.Do()

	mozilla()

	gnome()

	libreoffice()

	project = CompressedFileProject('abiword', 'http://www.abisource.com/dev/strings/dev/ca-ES.po', 'abiword-ca.po')
	project.Do() 

	ubuntu()

	os.system("msgfmt -c --statistics tm.po")

	print "Execution time:", time.time() - start_time, "seconds"

if __name__ == "__main__":
    main()


