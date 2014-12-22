#!/bin/bash

copy_files() {

    # Index
    rm -r -f $2/indexdir
    mkdir $2/indexdir
    cp -r $1/tm-git/src/web/indexdir/* $2/indexdir

    # Search TM app
    mkdir -p $2/css
    mkdir -p $2/img
    mkdir -p $2/templates

    cp $1/tm-git/src/web/css/recursos.css $2/css
    cp $1/tm-git/src/web/index.html $2
    cp $1/tm-git/src/web/web_search.py $2
    cp $1/tm-git/src/web/cleanupfilter.py $2
    cp $1/tm-git/src/web/statistics.html $2
    cp $1/tm-git/src/web/download.html $2
    cp $1/tm-git/src/web/select-projects.html $2
    cp $1/tm-git/src/web/robots.txt $2
    cp $1/tm-git/src/web/memories.html $2
    cp $1/tm-git/src/web/terminologia.html $2
    cp $1/tm-git/src/web/img/*.png $2/img
    cp $1/tm-git/src/web/templates/*.html $2/templates

    # Download memories
    cp $1/tm-git/src/web/download.html $2
    rm -r -f $2/memories
    mkdir $2/memories
    cp $1/tm-git/src/web/memories/*.zip $2/memories

    # Deploy terminology
    cd $1/tm-git/terminology
    cp *.html $2
    cp *.csv $2
}


if [ "$#" -ne 3 ] ; then
    echo "Usage: deploy.sh ROOT_DIRECTORY_OF_BUILD_LOCATION TARGET_DESTINATION TARGET_PREPROD"
    echo "Invalid number of parameters"
    exit
fi  

ROOT="$1"
TARGET_DIR="$2"
TARGET_PREPROD="$3"

# Run unit tests
cd $ROOT/tm-git/
nosetests
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "Aborting deployment. Unit tests did not pass"
    exit
fi

# Deploy to a pre-production environment where we can run integration tests
copy_files $ROOT $TARGET_PREPROD

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
