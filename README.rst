.. image:: https://travis-ci.org/Softcatala/translation-memory-tools.svg
    :target: https://travis-ci.org/Softcatala/translation-memory-tools

.. image:: https://coveralls.io/repos/Softcatala/translation-memory-tools/badge.png?branch=master
  :target: https://coveralls.io/r/Softcatala/translation-memory-tools?branch=master


============
Introduction
============

This is the toolset used at Softcatalà to build the translation memories for
all the projects that we contribute to.

The toolset performs the following tasks:

* Download and unpack the files from source repositories
* Create a translation memory for project in PO and TMX format
* Produce a single translation memory file that contains all the projects

`Web page of the project`_


Dependencies
============

* Python 2.7
* gettext
* Bazaar
* Subversion 1.7 or higher
* Git
* Other requirements listed in requirements.txt


Setting up before execution
===========================

For Transifex's project (all projects with type ``transifex`` at
``projects.json``) ask for credential at their Transifex servers the first
time that they get executed. After the first execution, they get recorded
in the ``.transifexrc`` file.


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

compare-sets.py (for reporting propouses)
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
   The unittest to check the funcitionality of different classes
   
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
