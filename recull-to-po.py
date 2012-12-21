#!/usr/bin/python2
#

import polib

cvsfile = open("recull.csv", "r")
pofile = polib.POFile()

pofile.metadata = {
	'Project-Id-Version': '1.0',
	'Report-Msgid-Bugs-To': 'info@softcatala.org',
	'POT-Creation-Date': '2007-10-18 14:00+0100',
	'PO-Revision-Date': '2007-10-18 14:00+0100',
	'Last-Translator': 'info@softcatala.org',
	'Language-Team': 'Catalan <info@softcatala.org>',
	'MIME-Version': '1.0',
	'Content-Type': 'text/plain; charset=utf-8',
	'Content-Transfer-Encoding': '8bit',
	'Plural-Forms' : 'nplurals=2; plural=n != 1;',
}

for line in cvsfile:
    columns = line.split(',')
    columns = [col.strip() for col in columns]

    if columns:
		if ((columns[2] == 'm' or columns[2] == 'f') and not '(' in columns[1] and not '|' in columns[1]):

			s = unicode(columns[0], 'utf-8')
			columns[0] = s[0].upper() + s[1:]

			s = unicode(columns[1], 'utf-8')
			columns[1] = s[0].upper() + s[1:]

	   		print columns[0] + "->" + columns[1] + "->" + columns[2]

			entry = polib.POEntry(
			msgid=columns[0],
		    msgstr=columns[1])
			pofile.append(entry)

pofile.save('recull.po');



