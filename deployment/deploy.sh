#!/bin/bash

copy_files() {

    # Index
    rm -r -f $2/indexdir
    mkdir -p $2/indexdir
    cp $1/tm-git/src/index_data.json $2

    # Download memories
    cp $1/tm-git/src/projects.json $2
    rm -r -f $2/memories
    mkdir $2/memories
    cp $1/tm-git/src/memories/*.zip $2/memories
    cp $1/tm-git/src/*error*.log $2/memories

    # Deploy terminology
    cd $1/tm-git/src/
    mkdir -p $2/terminology
    cp *glossary*.html $2/terminology
    cp *glossary*.csv $2/terminology
    cp sc-glossary.json $2/glossary.json

    # Deploy quality reports
    cd $1/tm-git/src/output/quality
    mkdir -p $2/quality
    cp *.html $2/quality
    mkdir -p $2/quality/img
    cd $1/tm-git/src/quality/img
    cp squ* $2/quality/img
}


if [ "$#" -ne 2 ] ; then
    echo "Usage: deploy.sh ROOT_DIRECTORY_OF_BUILD_LOCATION TARGET_DESTINATION"
    echo "Invalid number of parameters"
    exit
fi

ROOT="$1"
TARGET_DIR="$2"

# Deployment to production environment
copy_files $ROOT $TARGET_DIR

# Notify completion
INTERMEDIATE_PO=$TARGET_DIR/translation-memories/po
BACKUP_DIR=$TARGET_DIR/previous
cd $ROOT/tm-git/src
ls -h -s -S  $TARGET_DIR/quality/*.html
cat applications-error.log

echo "Deployment completed $ROOT $TARGET_DIR"
