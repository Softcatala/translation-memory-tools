#!/bin/bash

if [ "$#" -ne 1 ] ; then
    echo "Usage: generate-tm.sh ROOT_DIRECTORY_OF_BUILD_LOCATION"
    echo "Invalid number of parameters"
    exit
fi 

ROOT="$1"

if [ ! -z "$NOPOBUILD" ]; then
    echo "Skipping bulding of PO files"
fi

INTERMEDIATE_PO=$ROOT/translation-memories/po
INTERMEDIATE_TMX=$ROOT/translation-memories/tmx
PROGRAMS=$ROOT/tm-git/src
BACKUP_DIR=$ROOT/previous

# Catalan locale does not support thousand separator
export LC_ALL=ast_ES.utf-8

# Copy existing PO files
rm -r -f $BACKUP_DIR
mkdir $BACKUP_DIR
cd $BACKUP_DIR
cp $INTERMEDIATE_PO/* $BACKUP_DIR

if [ -z "$NOPOBUILD" ]; then
    cd $PROGRAMS
    rm -f *.po
    rm -f *.tmx
    rm -f *.log

    # Download new translation files
    python builder.py

    # Build aggregated memories
    cd $INTERMEDIATE_PO/
    python $PROGRAMS/builder.py -s $PROGRAMS/projects.json --all
    python $PROGRAMS/builder.py -s $PROGRAMS/projects.json --softcatala
    cp tots-tm.tmx $INTERMEDIATE_TMX/
    cp softcatala-tm.tmx $INTERMEDIATE_TMX/
fi

cd $PROGRAMS

# Copy only new PO files
for filename in *.po; do
    # If file exists and size is greater than 200 bytes
    if [ -e  $filename ]; then
        fsize=$(du -b "$filename" | cut -f 1)
        if [ $fsize -ge 200 ]; then
            if ! diff -q $filename $INTERMEDIATE_PO/$filename > /dev/null; then
                echo "Copying $filename"
                cp $filename $INTERMEDIATE_PO/$filename
            fi
        fi
    fi
done


# Copy only new TMX files
for filename in *.tmx; do
    # If file exists and size is greater than 350 bytes
    if [ -e  $filename ]; then
        fsize=$(du -b "$filename" | cut -f 1)
        # Empty TMX files are 275 bytes (just the header)
        # Files with one short translation 450 bytes
        if [ $fsize -ge 350 ]; then
            echo "Copying $filename"
            cp $filename $INTERMEDIATE_TMX/$filename
        fi
    fi
done

# Update download file & index
cd $PROGRAMS/web
python download-creation.py -d $INTERMEDIATE_PO -t $INTERMEDIATE_TMX
python index-creation.py -d $INTERMEDIATE_PO

# Notify completion
cd $PROGRAMS
pwd
python compare-sets.py -s  $BACKUP_DIR -t $INTERMEDIATE_PO 
