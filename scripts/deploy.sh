#!/bin/bash
TARGET_DIR=/var/www/recursos.softcatala.org/

# Index
rm -r -f $TARGET_DIR/indexdir
mkdir $TARGET_DIR/indexdir
cp -r tm-git/web/search/indexdir/* $TARGET_DIR/indexdir

# Search TM app
cp tm-git/web/apply_tm/recursos.css $TARGET_DIR
cp tm-git/web/search/index.html $TARGET_DIR
cp tm-git/web/search/web_search.py $TARGET_DIR
cp tm-git/web/search/statistics.html $TARGET_DIR
cp tm-git/web/download-memories/download.html $TARGET_DIR

# Download memories
cp tm-git/web/download-memories/download.html $TARGET_DIR
rm -r -f $TARGET_DIR/memories
mkdir $TARGET_DIR/memories
#cp translation-memories/po/*.po $TARGET_DIR/memories
#cp translation-memories/tmx/*.tmx $TARGET_DIR/memories
cp tm-git/web/download-memories/memories/*.zip $TARGET_DIR/memories
