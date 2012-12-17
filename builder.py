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

class DownloadFile:

	def GetFile(self, url, filename):
		
		print 'Downloading file \'' + url + '\''

		mp3file = urllib2.urlopen(url)
		output = open(filename,'wb')
		output.write(mp3file.read())
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
	
class ProcessProject():

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
			pofile.AddCommentToAllEntries(filename, "Translation source: " + relative +  " from project " + self.project)

	def Build(self):

		findFiles = FindFiles()

		os.system("rm -f tm.po")
		for filename in findFiles.Find(self.temp_dir, '*.po'):

			print 'Adding file:' + filename + ' to translation memory'

			if (os.path.isfile("tm.po")):
				os.system("cp tm.po tm-bak.po")
				os.system("msgcat -tutf-8 --use-first -o tm.po tm-bak.po " + filename)
			else:
				os.system("msgcat -tutf-8 --use-first -o tm.po " + filename)

		os.system("msgfmt -c --statistics tm.po")

	def Do(self):

		# Download po files
		download = DownloadFile()
		download.GetFile(self.url, self.filename)

		# Uncompress
		os.system("unzip libreoffice-help.zip -d " + self.temp_dir)

		self.AddComments()
		self.Build()


def main():

	print "Translation memory builder version 0.1"

	project = ProcessProject('LibreOffice.org', 'http://translations.documentfoundation.org/ca/libo36x_help/export/zip', 'libreoffice-help.zip');
	project.Do();

if __name__ == "__main__":
    main()


