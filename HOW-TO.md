#  Introduction

# Description of the system

The system reads all configuration files listed in [cfg/projects/](cfg/projects/)

# Sample configuration file

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

# Accessing non-public files & credentials

We always try to access public files, which require no user or password to download them. However, sometimes some _filesets_ require credentials to download the translation files. 
The credentials for these systems (e.g. Transifex, Weblate, etc) need to be properly configured credentials at [cfg/credentials/](cfg/credentials/)

In order to configure the credentials for these projects:
* You need to create an account on these projects (we cannot share our account)
* At [cfg/credentials/](cfg/credentials/) you need to copy the credentials configuration sample file (ends with *-sample*) to the final file (e.g. *cp zanata-sample.yaml zanata.yaml*)
* Store your credentials in the file

My advice:

* When possible, avoid to use Transifex or any system that requires credentials to access file , these are files that are not easily publically downloadable. Prefer direct downloads when available
* To be able to download the translations for a Transifex you need to be:
  * Member of the translation team
  * The translations memory user name will need to be also accepted

# Pattern field

Project configuration files can contain a _pattern_ which can be used to filter out files that you do not want to add to the translation memory.
This is useful when in the source there are translations for many languages but you only want process the Catalan files.
See the following fragment:

```
    "desktop-file-translationsdesktop-file-translations": {
        "url": "https://github.com/openSUSE/desktop-file-translations",
        "type": "git",
        "pattern": "-*?\/ca_ES\/.*.po"
}
```

The _pattern_ field is a Python regular expression. You can use sites like https://regex101.com/ to create and test regular expressions.

_Note: notice you need to scape the ```\``` char._

# Converting files

The system works internally using PO files, then all the files that downloads it tries to convert them to PO files. 

Before starting building the translation memory for a project (e.g. gnome-tm.po) the system tries to convert all the files that it found suitable for translation. At [src/builder/convertfiles.py](src/builder/convertfiles.py) you can see all the files and formats that are converted and which tools are used.

Some time some conversors need specific parameters for specific cases. For example, you may need to specify specific charset encoding for a file type. You can do so by adding a _conversor_setup_:

```
"fileset": {
    "LanguageTool": {
        "url": "https://app.transifex.com/dnaber/languagetool/",
        "type": "transifex",
        "po_preprocessing" : "remove_untranslated",
        "conversor_setup": {
            "type"       : "properties",
            "verb"       : "add",
            "command"    : " --encoding=utf-8"
        }
    }
```

The type parameter indicates to which conversor you want to add the additional parameters and command which parameters you want to add.

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
`Última baixada de la memòria`. If the date is older than a week, the system is unable to download the translations.

The most common reason is that the URL where the translations are published has changed.

At [https://static.softcatala.org/memories/applications-error.log](https://static.softcatala.org/memories/applications-error.log) you can see the logs of the last execution.

# Debugging issues

Setting the environment variable `LOGLEVEL` to `DEBUG` enables debug messages:

```
export LOGLEVEL="DEBUG"
```

If you are using macOS or Windows you will not see all debug messages because when starting new processes to download files in Linux Python uses `fork` which inherits
the logging handlers but in other platforms uses `spawn` that does not and prevents seeing all log messages. To prevent this in non-Linux systems define:

```
export SINGLE_THREAD_DOWNLOAD=1
```
