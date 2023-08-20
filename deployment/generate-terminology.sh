#!/bin/bash
echo Generate terminology
if [ "$#" -ne 1 ] ; then
    echo "Usage: generate-terminology.sh ROOT_DIRECTORY_OF_BUILD_LOCATION"
    echo "Invalid number of parameters"
    exit
fi 

ROOT="$1"

cd $ROOT/tm-git/src/

# Get files
rm -r -f sc-tm
mkdir sc-tm
unzip $ROOT/tm-git/src/memories/softcatala-tm.po.zip -d sc-tm/
rm -f sc-tm/softcatala-tm.po

rm -r -f tots-tm
mkdir tots-tm
unzip $ROOT/tm-git/src/memories/tots-tm.po.zip -d tots-tm/
rm -f tots-tm/tots-tm.po

# Build
python term_extract.py -s sc-tm -t sc-glossary -c "Glossari generat a partir de les memòries de traducció dels projectes traduïts per Softcatalà" 
python term_extract.py -s tots-tm -t tots-glossary -c "Glossari generat a partir de les memòries de de traducció de tots els projectes que podeu trobar a https://www.softcatala.org/recursos/memories/"
