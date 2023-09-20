#!/bin/bash
ROOT="$1"
PUBLIC="$2"
PROGRAMS=$ROOT/tm-git/src
BUILDER=$PROGRAMS
CHECK_LINKS=$ROOT/tm-git/integration-tests
NEW_POS=$PROGRAMS/output
# PUBLISHED directories are used to allow to publish the previous version if
# we have been unable to fetch it.
# This only works after the first successfully fetch when you have a previous
# copy of the successful executions
PUBLISHED_PO=$PUBLIC/translation-memories/po
PUBLISHED_TMX=$PUBLIC/translation-memories/tmx

copy_successfully_downloaded_files() {

    cd $NEW_POS
    # Copy only new PO files
    for filename in $1; do
        # If file exists and size is greater than 200 bytes
        if [ -e  "$filename" ]; then
            fsize=$(du -b "$filename" | cut -f 1)
            if [ $fsize -ge $2 ]; then
                if ! diff -q "$filename" "$3/$filename" > /dev/null; then
                    echo "Copying $filename"
                    cp "$filename" "$3/$filename"
                fi
            fi
        fi
    done
}

echo Generate memories
if [ "$#" -ne 2 ] ; then
    echo "Usage: generate-tm.sh ROOT_DIRECTORY_OF_BUILD_LOCATION PUBLIC_DATA"
    echo "Invalid number of parameters"
    exit
fi

export LC_ALL=ca_ES.utf-8

mkdir -p $PUBLISHED_PO
mkdir -p $PUBLISHED_TMX

# Check project links
cd $CHECK_LINKS
python run-check-links.py

# Build new translation files
cd $BUILDER
rm -f *.log
rm -f -r $NEW_POS

# Download new translation files
python builder.py -d
python builder.py --softcatala
cat $CHECK_LINKS/run-check-links-error.log >> builder-error.log

copy_successfully_downloaded_files "*.po" 200 $PUBLISHED_PO

# Empty TMX files are 275 bytes (just the header)
# Files with one short translation 450 bytes
copy_successfully_downloaded_files "*.tmx" 350 $PUBLISHED_TMX

# Update download file & index
cd $PROGRAMS
python download_creation.py -d $PUBLISHED_PO -t $PUBLISHED_TMX
python index_creation.py -d $NEW_POS
