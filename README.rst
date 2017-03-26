.. image:: https://travis-ci.org/Softcatala/translation-memory-tools.svg
    :target: https://travis-ci.org/Softcatala/translation-memory-tools

.. image:: https://coveralls.io/repos/Softcatala/translation-memory-tools/badge.png?branch=master
  :target: https://coveralls.io/r/Softcatala/translation-memory-tools?branch=master


============
Introduction
============

This is the toolset used at Softcatalà to build the translation memories for
all the projects that we know exist in Catalan language and have their
translations available openly.

The toolset contains the following components with their own responsibility:

Builder (fetch and build memories)
* Download and unpack the files from source repositories
* Convert from the different translation formats (ts, strings, etc) to PO
* Create a translation memory for project in PO and TMX formats
* Produce a single translation memory file that contains all the projects

Web
* Provides a web application and an API that allow users download memories
and search translation
* Provides an index-creator that creates a Whoosh index with all the strings
than then the user can search using the web app
* Provides an download-creation that creates a zip file with all memories that
the user can download

Terminology (terminology extraction)
* Analyzes the PO files and creates a report with the most common terminology
across the projects

Quality (feedback on how to improve translations)
* Runs Pology and LanguageTool and generates HTML reports on translation quality

`Web page of the project`_


Dependencies
============

* Python 3.4 or higher
* gettext
* Bazaar
* Subversion 1.7 or higher
* Git
* Ruby + (gem install i18n-translators-tools)
* Other requirements listed in requirements.txt


Setting up before execution
===========================

For Transifex's project (all projects with type ``transifex`` at
``projects.json``) ask for credential at their Transifex servers the first
time that they get executed. After the first execution, they get recorded
in the ``.transifexrc`` file.

`Flask configuration`_

Logging
=======

After the execution a ``builder.log`` file is created with details for
execution.


Projects included in the translation memory
===========================================

The file ``projects.json`` contains the description of the projects that
are included in the translation memory.

If context is not provided (msgctxt), duplicated translations are not stored.
As result, the first occurrence of a string is added to the memory,
ignoring the rest. For this reason the projects with better translations
are first in the json file.

The supported file types are: ``PO``, ``TS`` and ``.strings`` files (transifex
repositories only).


Applications
============

Located at ``src`` subdirectory:

builder.py (main program)
   Builds the translation memory: downloads files, merge them and builds the
   final translation memory

compare-sets.py (for reporting proposes)
   Compares two sets of the PO files and counts the words
    
Located at ``web`` subdirectory:

search 
   Scripts to create the Whossh index and enable the web application
   
download-memories
   Generates the web page to download the memories
   
scripts
   All the automation scripts to build the system automatically nightly

Located at root directory:

unittests
   The unittest to check the functionality of different classes
   
integration-tests
   tests that check if what has been generated contains errors 


Commands
========

Merging the translation memory with a new file::

    msgmerge -N tm.po new-pofile.po > final-pofile.po

You can also use translate-toolkit's pretranslate tool


Contact Information
===================

Jordi Mas: jmas@softcatala.org

.. _`Web page of the project`: http://www.softcatala.org/wiki/Memòria_traducció_de_Softcatalà
.. _`Flask configuration`: https://realpython.com/blog/python/kickstarting-flask-on-ubuntu-setup-and-deployment/

