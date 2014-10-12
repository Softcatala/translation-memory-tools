#!/bin/bash


echo "Deploy terminology"

TARGET_DIR=/var/www/recursos.softcatala.org/preprod
ROOT=/home/jmas

if [ ! -z "$DEVENV" ]; then
    ROOT=/home/jmas/dev
    echo "Development enviroment set to $TARGET_DIR"
fi

cd $ROOT/tm-git/terminology

# Get files
rm -r -f sc-tm
mkdir sc-tm
cd sc-tm
cp $ROOT/tm-git/web/memories/softcatala-tm.po.zip .
unzip softcatala-tm.po.zip
rm -f softcatala-tm.po
cd ..

rm -r -f tots-tm
mkdir tots-tm
cd tots-tm
cp $ROOT/tm-git/web/memories/tots-tm.po.zip .
unzip tots-tm.po.zip
rm -f tots-tm.po
cd ..

# Build
python term-extract.py -s sc-tm -t sc-glossary -c "Glossari generat a partir de les memòries de traducció dels projectes traduïts per Softcatalà" 
python term-extract.py -s tots-tm -t tots-glossary -c "Glossari generat a partir de les memòries de de traducció de tots els projectes que podeu trobar a http://www.softcatala.org/recursos/memories.html"


