#!/bin/bash
TARGET_DIR=/var/www/recursos.softcatala.org
ROOT=/home/jmas

if [ ! -z "$DEVENV" ]; then
    ROOT=/home/jmas/dev
    TARGET_DIR=/var/www/recursos.softcatala.org/dev
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
cp $ROOT/tm-git/web/download-memories/download.html $TARGET_DIR

# Download memories
cp $ROOT/tm-git/web/download-memories/download.html $TARGET_DIR
rm -r -f $TARGET_DIR/memories
mkdir $TARGET_DIR/memories
cp $ROOT/tm-git/web/download-memories/memories/*.zip $TARGET_DIR/memories
cp $ROOT/tm-git/src/report.txt $TARGET_DIR
