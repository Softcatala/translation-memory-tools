#!/bin/bash

if [ -z "$DEVENV" ]; then
    echo Not ready for production yet 
    exit
fi

echo Deploy terminology
ROOT=/home/jmas/dev
TARGET_DIR=/var/www/recursos.softcatala.org/dev/terminologia

cd $ROOT/tm-git/terminology

# Get files
cd sc-tm
rm *.po
cp $ROOT/tm-git/web/search/memories/softcatala-tm.po.zip .
unzip softcatala-tm.po.zip
rm -f softcatala-tm.po
cd ..

cd all-tm
rm *.po
cp $ROOT/tm-git/web/search/memories/tots-tm.po.zip .
unzip tots-tm.po.zip
rm -f tots-tm.po
cd ..

# Build
python term-extract.py -s sc-tm -t sc-glossary -c "Glossari construït a partir de les memòries de traducció dels projectes traduïts per Softcatalà" 
python term-extract.py -s all-tm -t all-glossary -c "Glossari construït a partir de les memòries de de traducció de tots els projectes que podeu trobar a http://www.softcatala.org/recursos/memories.html"

# Deploy
cp *.html $TARGET_DIR
cp *.csv $TARGET_DIR
