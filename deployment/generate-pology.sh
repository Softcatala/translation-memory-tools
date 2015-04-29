#!/bin/bash

ROOT="$1"
POLOGY=$ROOT/tm-git/pology/
POLOGY_OUTPUT=$ROOT/tm-git/src/pology

rm -r -f $POLOGY_OUTPUT
mkdir $POLOGY_OUTPUT

cd $ROOT/tm-git/src/terminology
cd tots-tm

for filename in *.po; do
    echo "Executing posieve on: " $filename
    posieve set-header -sfield:'Language:ca' -screate $filename 
    cat $POLOGY/header.html > $POLOGY_OUTPUT/$filename.html
    posieve --skip-obsolete --coloring-type=html check-rules -s rfile:$POLOGY/false-friends.rules -s rfile:$POLOGY/keys.rules $filename >> $POLOGY_OUTPUT/$filename-temp.html

    if [ -s  $POLOGY_OUTPUT/$filename-temp.html ] ; then
        cat $POLOGY_OUTPUT/$filename-temp.html >> $POLOGY_OUTPUT/$filename.html
    else
        echo "No s'ha detectat cap error." >> $POLOGY_OUTPUT/$filename.html 
    fi
    rm -r -f $POLOGY_OUTPUT/$filename-temp.html
    cat $POLOGY/footer.html >> $POLOGY_OUTPUT/$filename.html
done



