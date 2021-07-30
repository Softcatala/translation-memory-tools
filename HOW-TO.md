#  Introduction

## Description of the system

The system reads all configuration files listed in [cfg/projects/](cfg/projects/)

## Sample configuration file

Take as an example a file the file defining the [cfg/projects/Git.json](cfg/projects/Git.json) project:

```
{
    "project": "Git", 
    "projectweb": "https://www.softcatala.org/projectes/git/",
    "softcatala": true,
    "fileset": {
        "Git": {
            "url": "https://raw.githubusercontent.com/Softcatala/git-po/master/po/ca.po",
            "type": "file",
            "target": "ca.po"
        },
        "Git-k": {
            "url": "https://raw.githubusercontent.com/Softcatala/git-po/master/gitk-git/po/ca.po",
            "type": "file",
            "target": "ca.po"
        }
    }
}
```

Some concepts here:
* A project can contain multiple _filesets_.
* The _filesets_ can be of various types: transifex, git, svn, etc. In the _add_filesets_ method at [src/builder/project.py](src/builder/project.py) you can see the code that handles them

## Accessing non-public files

We always try to access public files, but sometimes some _filesets_ need credentials to access the remote files. 
There are some cases filesets that need properly configured credentials at [cfg/credentials/](cfg/credentials/)

However, Transifex is the most common one with over 100 projects using it. My advice:

* Avoid to use Transifex when possible, these are files that are not easily publically downloadable. Prefer direct downloads when available
* To be able to download the translations for a Transifex you need to be:
  * Member of the translation team
  * The translations memory user name will need to be also accepted

## Converting files

The system works internally using PO files, then all the files that downloads it tries to convert them to PO files. 

Before starting building the translation memory for a project (e.g. gnome-tm.po) the system tries to convert all the files that it found suitable for translation. At [src/builder/convertfiles.py](src/builder/convertfiles.py) you can see all the files and formats that are converted and which tools are used.

# Adding a new project to the system

The easiest approach to add a new project to the system is look for a similar one and use that configuration file as starting point.

Once you have your configuration file, you need to test the file. Imagine that your project it's called `Abiword`, then you need to do:

```
cd src
python3 builder.py -pAbiword
```

This will generate the file `./output/abiword-tm.po`. You need to check that the file is correct, in particular:
* Includes all the translations
* The encoding is correct and special characters are represented properly

Once you have a new working project, you can summit it by doing a pull request to the Git repository.

# Fixing an already existing project

Go to [https://www.softcatala.org/recursos/memories/](https://www.softcatala.org/recursos/memories/) and check the date in the field 
`Última baixada de la memòria`. If the date is older than a week, the system is unable to download your memory. 

Most common reason is that has changed the URL where it publishes the translations.

At [https://static.softcatala.org/memories/builder-error.log](https://static.softcatala.org/memories/builder-error.log) you can see the logs of the last execution.

