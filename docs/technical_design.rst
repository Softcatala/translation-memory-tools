================
Technical design
================

Libraries
=========

We use two data storage backends:

* `Whoosh`_ as full-text indexing and searching over the translation memories. 
* `SQLite`_ as relational backend to keep track of statistics related to the translation memories built (latest fetch date, etc)

We use `Mustache`_ as template engine to generate outputs from source code to prevent mixing data and its representation.

Downloading, converting and building translation memories
=========================================================

builder.py launches the process to download and build the translation memories. The output is a set of PO and TMX files and a database with statistics of the files generated.

The file projects.json contains a definition of the projects for which we build the translation memories

Every project can contain a group of filesets. We support serveral fetch mecanisms 

The process of building a transtlation memories works as follows:

* Every fileset is downloaded using its downloaded mecanism (git, svn, file download, etc)
* All the files download (e.g ts, xml, etc) are converted to PO (the interal format to build the memories)
* All the segments are added a comment that indicates where the translation was imported from
* Translations memories are build using GNU Text (msgcat)
* When the process is finished we generate a TMX from the PO file

Limations:
* msgcat is slow with large files (e.g. KDE or GNOME)
* To convert to PO we use the translation toolkit. For XML you need to specify the format but we do not.
* PO as native format is limited. For example, to indicate the source of the translation (we use a comment)

Searchable index
================

The file index-creation.py reads a set of PO files (translation memories) and builds a full text Whoosh index.

This index is used by the Web application.

The searchable index can be queried using JSON, using a this URL format '{0}/web_search.py?source={1}&project=tots&json=1'

Terminology extraction
======================

The term-extract.py application run the terminology extraction module. It takes a set of PO files as source files, selects terminology and then generates a report in serveral formats (like HTML).

It uses term frequency to select the most common used terms. It uses serveral PO files to as quality measures of the output provided. 

Limitations:

* It only analyzes segments of 3 words to avoid having to align terms in sentences (a complex problem)
* It does not recognizes derived forms like plurals or verbs tenses (it could be done easily using NLK) 

.. _`Whoosh`: https://pypi.python.org/pypi/Whoosh/
.. _`SQLite`: http://www.sqlite.org/
.. _`Mustache`: http://mustache.github.io/

