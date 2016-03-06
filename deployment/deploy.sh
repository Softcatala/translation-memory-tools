#!/bin/bash

copy_files() {

    #Softcatalà headers and footers
    rm -r -f $2/ssi
    mkdir $2/ssi
    cp -r $1/web-Softcatala/ssi/* $2/ssi

    # Index
    rm -r -f $2/indexdir
    mkdir $2/indexdir
    cp -r $1/tm-git/src/web/indexdir/* $2/indexdir

    # Search TM app
    mkdir -p $2/css
    mkdir -p $2/img
    mkdir -p $2/templates
    mkdir -p $2/models
    mkdir -p $2/chosen

    cp $1/tm-git/src/web/css/recursos.css $2/css
    cp $1/tm-git/src/web/index.html $2
    cp $1/tm-git/src/web/web_search.py $2
    cp $1/tm-git/src/web/cleanupfilter.py $2
    cp $1/tm-git/src/web/header.html $2
    cp $1/tm-git/src/web/footer.html $2
    cp $1/tm-git/src/web/statistics.html $2
    cp $1/tm-git/src/web/download.html $2
    cp $1/tm-git/src/web/select-projects.html $2
    cp $1/tm-git/src/web/robots.txt $2
    cp $1/tm-git/src/web/memories.html $2
    cp $1/tm-git/src/web/terminologia.html $2
    cp $1/tm-git/src/web/llistats_iso.html $2
    cp $1/tm-git/src/web/img/*.png $2/img
    cp $1/tm-git/src/web/templates/*.html $2/templates
    cp $1/tm-git/src/web/models/*.py $2/models
    cp $1/tm-git/src/terminology/glossarysql.py $2/models
    cp -r $1/tm-git/src/web/chosen/* $2/chosen

    # Web dependencies
    mkdir $2/builder
    cp $1/tm-git/src/builder/cleanupfilter.py $2/builder


    # Download memories
    cp $1/tm-git/src/download.html $2
    rm -r -f $2/memories
    mkdir $2/memories
    cp $1/tm-git/src/memories/*.zip $2/memories
    cp $1/tm-git/src/tots-pos.zip $2/memories

    # Deploy terminology
    cd $1/tm-git/src/terminology
    cp *.html $2
    cp *.csv $2
    cp sc-glossary.db3 $2/glossary.db3

    # Deploy quality reports
    cd $1/tm-git/quality
    rm -r -f $2/quality
    mkdir $2/quality
    cp *.html $2/quality

    # ISO lists
    cp $1/tm-git/src/isolists/*.html $2

    # Log
    rm -r -f $2/logs
    mkdir $2/logs
    cp $1/tm-git/quality/*.log $2/logs
    cp $1/tm-git/src/*.log $2/logs
}

restart_appserver() {
    sudo supervisorctl stop recursos_preprod
    sudo supervisorctl stop recursos_dev
    sudo supervisorctl stop recursos
    sudo supervisorctl start recursos_preprod
    sudo supervisorctl start recursos_dev
    sudo supervisorctl start recursos
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
restart_appserver

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
restart_appserver

# Notify completion
INTERMEDIATE_PO=$ROOT/translation-memories/po
BACKUP_DIR=$ROOT/previous
cd $ROOT/tm-git/src/builder
python compare-sets.py -s  $BACKUP_DIR -t $INTERMEDIATE_PO
cat builder-error.log

echo "Deployment completed $ROOT $TARGET_DIR"
