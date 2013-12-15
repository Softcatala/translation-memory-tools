#!/bin/bash

#
# Build a pre-production enviroment where we can run integration tests
#

TARGET_DIR=/var/www/recursos.softcatala.org/preprod
ROOT=/home/jmas

if [ ! -z "$DEVENV" ]; then
    ROOT=/home/jmas/dev
    echo Development enviroment set to $TARGET_DIR
fi

# Index
rm -r -f $TARGET_DIR/indexdir
mkdir $TARGET_DIR/indexdir
cp -r $ROOT/tm-git/web/search/indexdir/* $TARGET_DIR/indexdir

# Search TM app
cp $ROOT/tm-git/web/search/recursos.css $TARGET_DIR
cp $ROOT/tm-git/web/search/index.html $TARGET_DIR
cp $ROOT/tm-git/web/search/web_search.py $TARGET_DIR
cp $ROOT/tm-git/web/search/statistics.html $TARGET_DIR
cp $ROOT/tm-git/web/search/download.html $TARGET_DIR
cp $ROOT/tm-git/web/search/select-projects.html $TARGET_DIR

# Download memories
cp $ROOT/tm-git/web/search/download.html $TARGET_DIR
rm -r -f $TARGET_DIR/memories
mkdir $TARGET_DIR/memories
cp $ROOT/tm-git/web/search/memories/*.zip $TARGET_DIR/memories
cp $ROOT/tm-git/src/report.txt $TARGET_DIR

# Run integration tests
cd $ROOT/tm-git/integration-tests/
python run.py -e preprod

RETVAL=$?
if [ $RETVAL -ne 0 ]; then 
   echo Aborting deployment
   exit
fi

#
# Deployment of final version
# 

TARGET_DIR=/var/www/recursos.softcatala.org
ROOT=/home/jmas

if [ ! -z "$DEVENV" ]; then
    ROOT=/home/jmas/dev
    TARGET_DIR=/var/www/recursos.softcatala.org/dev
fi

# Index
rm -r -f $TARGET_DIR/indexdir
mkdir $TARGET_DIR/indexdir
cp -r $ROOT/tm-git/web/search/indexdir/* $TARGET_DIR/indexdir

# Search TM app
cp $ROOT/tm-git/web/search/recursos.css $TARGET_DIR
cp $ROOT/tm-git/web/search/index.html $TARGET_DIR
cp $ROOT/tm-git/web/search/web_search.py $TARGET_DIR
cp $ROOT/tm-git/web/search/statistics.html $TARGET_DIR
cp $ROOT/tm-git/web/search/download.html $TARGET_DIR
cp $ROOT/tm-git/web/search/select-projects.html $TARGET_DIR
cp $ROOT/tm-git/web/search/robots.txt $TARGET_DIR


# Download memories
cp $ROOT/tm-git/web/search/download.html $TARGET_DIR
rm -r -f $TARGET_DIR/memories
mkdir $TARGET_DIR/memories
cp $ROOT/tm-git/web/search/memories/*.zip $TARGET_DIR/memories
cp $ROOT/tm-git/src/report.txt $TARGET_DIR

echo Deployment completed
