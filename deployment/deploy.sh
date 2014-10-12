#!/bin/bash

#
# Build a pre-production enviroment where we can run integration tests
#

TARGET_DIR=/var/www/recursos.softcatala.org/preprod
ROOT=/home/jmas

if [ ! -z "$DEVENV" ]; then
    ROOT=/home/jmas/dev
    echo "Development enviroment set to $TARGET_DIR"
fi


# Index
rm -r -f $TARGET_DIR/indexdir
mkdir $TARGET_DIR/indexdir
cp -r $ROOT/tm-git/web/indexdir/* $TARGET_DIR/indexdir

# Search TM app
cp $ROOT/tm-git/web/recursos.css $TARGET_DIR
cp $ROOT/tm-git/web/index.html $TARGET_DIR
cp $ROOT/tm-git/web/web_search.py $TARGET_DIR
cp $ROOT/tm-git/web/cleanstring.py $TARGET_DIR
cp $ROOT/tm-git/web/cleanupfilter.py $TARGET_DIR
cp $ROOT/tm-git/web/statistics.html $TARGET_DIR
cp $ROOT/tm-git/web/download.html $TARGET_DIR
cp $ROOT/tm-git/web/select-projects.html $TARGET_DIR
cp $ROOT/tm-git/web/robots.txt $TARGET_DIR
cp $ROOT/tm-git/web/memories.html $TARGET_DIR
cp $ROOT/tm-git/web/terminologia.html $TARGET_DIR
cp $ROOT/tm-git/web/*.png $TARGET_DIR


# Download memories
cp $ROOT/tm-git/web/download.html $TARGET_DIR
rm -r -f $TARGET_DIR/memories
mkdir $TARGET_DIR/memories
cp $ROOT/tm-git/web/memories/*.zip $TARGET_DIR/memories
cp $ROOT/tm-git/src/report.txt $TARGET_DIR

# Run unit tests
cd $ROOT/tm-git/unittests/
nosetests
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
    echo "Aborting deployment. Unit tests did not pass"
    exit
fi

# Run integration tests
cd $ROOT/tm-git/integration-tests/
python run.py -e preprod

RETVAL=$?
if [ $RETVAL -ne 0 ]; then 
    echo "Aborting deployment. Integration tests did not pass"
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

#Softcatalà headers and footers
cp $ROOT/mediawiki-Softcatala/ssi/header.html $TARGET_DIR
cp $ROOT/mediawiki-Softcatala/ssi/footer-g.html $TARGET_DIR

# Index
rm -r -f $TARGET_DIR/indexdir
mkdir $TARGET_DIR/indexdir
cp -r $ROOT/tm-git/web/indexdir/* $TARGET_DIR/indexdir

# Search TM app
cp $ROOT/tm-git/web/recursos.css $TARGET_DIR
cp $ROOT/tm-git/web/index.html $TARGET_DIR
cp $ROOT/tm-git/web/web_search.py $TARGET_DIR
cp $ROOT/tm-git/web/cleanstring.py $TARGET_DIR
cp $ROOT/tm-git/web/cleanupfilter.py $TARGET_DIR
cp $ROOT/tm-git/web/statistics.html $TARGET_DIR
cp $ROOT/tm-git/web/download.html $TARGET_DIR
cp $ROOT/tm-git/web/select-projects.html $TARGET_DIR
cp $ROOT/tm-git/web/robots.txt $TARGET_DIR
cp $ROOT/tm-git/web/memories.html $TARGET_DIR
cp $ROOT/tm-git/web/terminologia.html $TARGET_DIR
cp $ROOT/tm-git/web/*.png $TARGET_DIR


cp $ROOT/tm-git/web/download.html $TARGET_DIR
rm -r -f $TARGET_DIR/memories
mkdir $TARGET_DIR/memories
cp $ROOT/tm-git/web/memories/*.zip $TARGET_DIR/memories
cp $ROOT/tm-git/src/report.txt $TARGET_DIR

# Deploy terminology
cd $ROOT/tm-git/terminology
cp *.html $TARGET_DIR
cp *.csv $TARGET_DIR

echo "Deployment completed"
