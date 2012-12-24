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

		return;
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

class FileSet():

	temp_dir = "./tmp"

	def __init__(self, project, url, filename):
		self.project = project
		self.url = url
		self.filename = filename
		self.excluded = list()

	def SetTMFile(self, tmfile):
		self.tmfile = tmfile

	def AddExcluded(self, filename):
		self.excluded.append(filename)

	def AddComments(self):

		findFiles = FindFiles()

		for filename in findFiles.Find(self.temp_dir, '*.po'):
			relative = filename.replace(self.temp_dir, '')
			print 'Adding source reference to file:' + relative
			pofile = POFile()
			pofile.AddCommentToAllEntries(filename, "Translation source: " + relative +  " from project '" + self.project + "'")

	def CleanUp(self):
		os.system("cp " + self.tmfile +" tm-project-previous.po")
		os.system("msgattrib tm-project-previous.po --no-fuzzy --no-obsolete --translated > " + self.tmfile)
		os.system("rm -f tm-project-previous.po")
		
	def Build(self):

		findFiles = FindFiles()
		localtm = "tm-local.po"

		if (os.path.isfile(localtm)):
			os.system("rm -f " + localtm)

 		# Build using a local memory translation file
		for filename in findFiles.Find(self.temp_dir, '*.po'):

			exclude = False
			for exfilename in self.excluded:
				if (filename.find(exfilename) != -1):
					exclude = True

			if (exclude == True):
				print 'Excluding file:' + filename
				continue

			print 'Adding file:' + filename + ' to translation memory'

			if (os.path.isfile(localtm)):
				os.system("cp " + localtm + " tm-project-previous.po")
				os.system("msgcat -tutf-8 --use-first -o " + localtm + " tm-project-previous.po " + filename)
				os.system("rm -f tm-project-previous.po")
			else:
				os.system("cp " + filename + " " + localtm)

		# Add to the project TM
		if (os.path.isfile(self.tmfile)):
			os.system("cp " + self.tmfile + " tm-project-previous.po")
			os.system("msgcat -tutf-8 --use-first -o " + self.tmfile + " tm-project-previous.po " + localtm)
			os.system("rm -f tm-project-previous.po")
		else:
			os.system("cp " + localtm + " " + self.tmfile)

		os.system("rm -f " + localtm)
		self.CleanUp()

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


class CompressedFileSet(FileSet):

	def Do(self):

		# Download po files
		download = DownloadFile()
		download.GetFile(self.url, self.filename)

		self.Uncompress();
		self.AddComments()
		self.Build()

		os.system("rm -f " + self.filename)

class LocalFileSet(FileSet):

	def Do(self):

		os.system("cp " + self.url + " " + self.filename)

		self.Uncompress();
		self.AddComments()
		self.Build()

		os.system("rm -f " + self.filename)

class LocalDirFileSet(FileSet):

	def Do(self):

		os.system("rm -f " + self.temp_dir)
		os.system("mkdir " + self.temp_dir)
		os.system("cp " + self.url + " " + self.temp_dir +  "/" + self.filename)

		self.AddComments()
		self.Build()

class BazaarFileSet(FileSet):

	def Do(self):

		os.system("rm -r -f " + self.temp_dir)
		os.system("mkdir " + self.temp_dir)
		os.system("cd " + self.temp_dir)
		os.system(self.url + " > ca.po")

		self.Uncompress();
		self.AddComments()
		self.Build()

		os.system("rm -f ca.po")
		os.system("rm -r -f " + self.temp_dir)


class TransifexFileSet(FileSet):

	def Do(self):

		prevdir = os.getcwd()

		os.system("rm -r -f " + self.temp_dir)
		os.system("mkdir " + self.temp_dir)
		os.chdir(self.temp_dir)
		os.system("tx init --host https://fedora.transifex.net")
		os.system("tx set --auto-remote " + self.url)
		os.system("tx pull -f -lca")
		os.chdir(prevdir)

		self.AddComments()
		self.Build()

		os.system("rm -r -f " + self.temp_dir)



