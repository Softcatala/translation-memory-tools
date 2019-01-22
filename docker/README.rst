============
Introduction
============

The dockerfile-builder container downloads all the translation memories and
publishes the output files into a volume.

There is currently no Docker for the web app.

========
Commands
========

Create builder image:

``docker build -t tmt-builder . -f dockerfile-builder``

Simple execution of the builder image:

``docker run -v ~/tmt-public:/public-data -i -t tmt-builder``

Where ``~/tmt-public`` is the local directory in your host where the files
will be published

Since you are not providing credentials for Transifex o Zenata the projects
of this type will not be build. You need credentials in these systems.
Additionally for  Transifex you need to be member of all projects that you
want to download  since this is how they manage authorization to download
translations.

Complete execution of the builder image with credentials:

``docker run  --env TRANSIFEX_USER='XXXX' --env TRANSIFEX_PASSWORD='XXXX' --env TRANSIFEX_TOKEN='XXXX' --env ZANATA_PROJECT_1='OpenStack' --env ZANATA_USER_1='XXXX' --env ZANATA_TOKEN_1='XXXX' --env ZANATA_PROJECT_2='Fedora' --env ZANATA_USER_2='XXXX' --env ZANATA_TOKEN_2='XXXX'  -t tmt-builder``
