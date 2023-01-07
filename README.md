[![Python application](https://github.com/Softcatala/translation-memory-tools/actions/workflows/run-tests.yml/badge.svg)](https://github.com/Softcatala/translation-memory-tools/actions/workflows/run-tests.yml)

# Introduction

This is the toolset used at Softcatalà to build the translation memories for all the projects that we know exist in Catalan language and have their translations available openly. You can see it on-line at <https://www.softcatala.org/recursos/memories/>

The toolset contains the following components with their own responsibility:

**Builder** (fetch and build memories)

- Download and unpack the files from source repositories
- Convert from the different translation formats (ts, strings, etc) to PO
- Create a translation memory for project in PO and TMX formats
- Produce a single translation memory file that contains all the projects

**Web**

- Provides an API that allow users download memories and search translations
- Provides an index-creator that creates a Whoosh index with all the strings than then the user can search using the web app
- Provides an download-creation that creates a zip file with all memories that the user can download

**Terminology** (terminology extraction)

- Analyzes the PO files and creates a report with the most common terminology across the projects

**Quality** (feedback on how to improve translations)

- Runs Pology and LanguageTool and generates HTML reports on translation quality

# Installation

## Setting up before execution

In order to download the translations of some of the projects you need to use the credentials for these systems, for example API keys.

*builder.py* expects the credentials to be defined at [cfg/credentials](./cfg/credentials) in the diferent YML files for each one of the sites that require crendentials.

If you use docker locally or in production, these credetials are configured in a enviorment variables than then are used to created the configuration YML files.

## Runing the builder code locally

This part focuses on helping you to run the *builder* component locally in case that you want to test quickly new projects configurations. For any other use case, we recommend using the Docker.

```shell
sudo apt-get update -y && sudo apt-get install python3-dev libhunspell-dev libyaml-dev gettext zip mercurial bzr ruby git curl wget g++ subversion bzip2 python2-dev -y
curl -o- https://raw.githubusercontent.com/transifex/cli/master/install.sh | bash && mv ./tx /usr/bin/
sudo gem install i18n-translators-tools

cd translation-memory-tools
pip install -r requirements.txt
```

For example, to download only the Abiword project:

```shell
cd src
./builder.py -p Abiword
```

## Running the system locally using Docker

This requires that you have *docker*, *docker-compose* and *make* installed in your system.

First download the data for the projects and generate the data quality reports:

```shell
make docker-builder-run
```

Downloading all the projects can take up to a day, which is not acceptable for a development cycle. In the [docker/local.yml](./docker/local.yml) the variable *DEV_SMALL_SET* forces to only download some projects. This small subset does not requiere any specific credentials to be defined to download them.

The output files are copied to *web-docker* local directory to make easy to for you explore the results.

To run the web app which provides the microservices for the web site:

```shell
make docker-webapp-run
```

To test it from the browser:
* List projects: http://localhost:8080/projects


# Contributing

If you are looking at how to contribute to the project see [HOW-TO.md](HOW-TO.md)

# Contact Information

Jordi Mas: <jmas@softcatala.org>
