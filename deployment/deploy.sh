#!/bin/bash

copy_files() {

    ROOT="$1"
    TARGET_DIR="$2"

    #Softcatalà headers and footers
    cp $ROOT/mediawiki-Softcatala/ssi/header.html $TARGET_DIR
    cp $ROOT/mediawiki-Softcatala/ssi/footer-g.html $TARGET_DIR

    # Index
    rm -r -f $TARGET_DIR/indexdir
    mkdir $TARGET_DIR/indexdir
    cp -r $ROOT/tm-git/src/web/indexdir/* $TARGET_DIR/indexdir

    # Search TM app
    cp $ROOT/tm-git/src/web/recursos.css $TARGET_DIR
    cp $ROOT/tm-git/src/web/index.html $TARGET_DIR
    cp $ROOT/tm-git/src/web/web_search.py $TARGET_DIR
    cp $ROOT/tm-git/src/web/cleanstring.py $TARGET_DIR
    cp $ROOT/tm-git/src/web/cleanupfilter.py $TARGET_DIR
    cp $ROOT/tm-git/src/web/statistics.html $TARGET_DIR
    cp $ROOT/tm-git/src/web/download.html $TARGET_DIR
    cp $ROOT/tm-git/src/web/select-projects.html $TARGET_DIR
    cp $ROOT/tm-git/src/web/robots.txt $TARGET_DIR
    cp $ROOT/tm-git/src/web/memories.html $TARGET_DIR
    cp $ROOT/tm-git/src/web/terminologia.html $TARGET_DIR
    cp $ROOT/tm-git/src/web/*.png $TARGET_DIR

    # Download memories
    cp $ROOT/tm-git/src/web/download.html $TARGET_DIR
    rm -r -f $TARGET_DIR/memories
    mkdir $TARGET_DIR/memories
    cp $ROOT/tm-git/src/web/memories/*.zip $TARGET_DIR/memories
    cp $ROOT/tm-git/src/report.txt $TARGET_DIR

    # Deploy terminology
    cd $ROOT/tm-git/terminology
    cp *.html $TARGET_DIR
    cp *.csv $TARGET_DIR
}


if [ "$#" -ne 2 ] ; then
    echo "Usage: deploy.sh ROOT_DIRECTORY_OF_BUILD_LOCATION TARGET_DESTINATION"
    echo "Invalid number of parameters"
    exit
fi  

ROOT="$1"
TARGET_DIR="$2"

if [ ! -z "$DEVENV" ]; then
    ROOT=$ROOT/dev
    TARGET_DIR=$TARGET_DIR/dev
    echo "Development enviroment set to $ROOT"
fi

# Run unit tests
cd $ROOT/tm-git/unittests/
nosetests
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "Aborting deployment. Unit tests did not pass"
    exit
fi

# Deploy to a pre-production environment where we can run integration tests
copy_files $ROOT "$2"/preprod

# Run integration tests
cd $ROOT/tm-git/integration-tests/
python run.py -e preprod

RETVAL=$?
if [ $RETVAL -ne 0 ]; then 
    echo "Aborting deployment. Integration tests did not pass"
    exit
fi

# Deployment to production environment
copy_files $ROOT $TARGET_DIR

echo "Deployment completed"
