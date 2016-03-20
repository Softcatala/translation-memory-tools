#!/bin/bash

if [ "$#" -ne 1 ] ; then
    echo "Usage: generate-terminology.sh ROOT_DIRECTORY_OF_BUILD_LOCATION"
    echo "Invalid number of parameters"
    exit
fi 

ROOT="$1"

cd $ROOT/tm-git/src/terminology

# Get files
rm -r -f sc-tm
mkdir sc-tm
cd sc-tm
cp $ROOT/tm-git/src/memories/softcatala-tm.po.zip .
unzip softcatala-tm.po.zip
rm -f softcatala-tm.po
cd ..

rm -r -f tots-tm
mkdir tots-tm
cd tots-tm
cp $ROOT/tm-git/src/memories/tots-tm.po.zip .
unzip tots-tm.po.zip
rm -f tots-tm.po
cd ..

# Build
python term-extract.py -s sc-tm -t sc-glossary -c "Glossari generat a partir de les memòries de traducció dels projectes traduïts per Softcatalà" 
python term-extract.py -s tots-tm -t tots-glossary -c "Glossari generat a partir de les memòries de de traducció de tots els projectes que podeu trobar a http://www.softcatala.org/recursos/memories.html"
