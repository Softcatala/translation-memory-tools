# Introduction

This document describes Softcatalà's Gitlab CI/CD system to deploy the system in production.

# Pipelines 

## [github/translation-memory-tools](https://gitlab.softcatala.org/github/translation-memory-tools)

Responsibilities:

* Builds the image that will fetch the translation memories, generates terminology and quality reports
* Runs the image that fetches the translation memories

Storage:

* The docker volume volume _/srv/volumes/tmt-files_ is used to preserve the data between executions of the pipeline.

Once the _run_ job finishes, a Docker image based on _softcatala/sc-static-file-server_ is created to store all the data.

This image serves two purposes:
* Contains the information that will be used by the web app 
* It contains the static files which will be served at https://static.softcatala.org. These static files include:
  * the HTML quality reports, 
  * the terminology web/csv 
  * files and the translation memories (PO/TMX).
  * the index_data.json to later create a searchable index
  * the glossary.json to later create a searchable glossary / terminology


## [translation-memory-tools-webservice](https://gitlab.softcatala.org/github/translation-memory-tools-webservice)

Responsibilities:

* Create the Whoosh searchable index
* Builds the web app 
* Executes integration tests

## [docker/translation-memory-tools](https://gitlab.softcatala.org/docker/translation-memory-tools)

Contains the _docker-compose.yml_ used to run the system in production.

# Common tasks and troubleshooting with CI/CD

## Deploy a Git branch

There is no staging environment, you need to deploy your branches in pro.

To do this:

* Build the translation-memory-tools and translation-memory-tools-webservice branches. They will generate docker images tagged with the branch name
* Go to https://gitlab.softcatala.org/docker/translation-memory-tools and change the docker-compose.yml file to use the right branch

## Rolling back to a previous version

Go to https://gitlab.softcatala.org/docker/translation-memory-tools and change the docker-compose.yml file to a previous branch.

All the branches at tagged also with the date, such as _20231115-100154_ to enable to rollback to a specific date.

## Downloading the generated data image from translation-memory-tools

In the translation-memory-tools repo, use this Makefile task:

```shell
make docker-run-gitlab-data-debug
```
The image will be downloaded locally and you will login into the image which will allow you to inspect the data image generated



