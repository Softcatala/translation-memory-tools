#!/bin/bash
ROOT=/home/jmas/
INTERMEDIATE_PO=/home/jmas/translation-memories/po
INTERMEDIATE_TMX=/home/jmas/translation-memories/tmx
PROGRAMS=/home/jmas/tm-git/src
PROD_DIR=/var/www/recursos.softcatala.org/

# Download new translation files
cd $PROGRAMS
rm -f *.po
rm -f *.tmx
rm -f *.log
python builder.py

# Copy only new PO files
for filename in *.po
  do
    # If file exists and size is greater than 200 bytes
    if [ -e  $filename ]
      then
        fsize=$(du -b "$filename" | cut -f 1)
        if [ $fsize -ge 200 ];
          then
            echo Copying $filename
	    cp $filename $INTERMEDIATE_PO/$filename
        fi 
    fi
  done


# Copy only new TMX files
for filename in *.tmx
  do
    # If file exists and size is greater than 200 bytes
    if [ -e  $filename ]
      then
        fsize=$(du -b "$filename" | cut -f 1)
        if [ $fsize -ge 200 ];
          then
            echo Copying $filename
            cp $filename $INTERMEDIATE_TMX/$filename
        fi
    fi
  done


# Build aggregated memories
cd $INTERMEDIATE_PO/
python $PROGRAMS/builder.py -s $PROGRAMS/projects.json --all
python $PROGRAMS/builder.py -s $PROGRAMS/projects.json --softcatala
cp *.tmx ../tmx/

# Update download file & index
cd /home/jmas/tm-git/web/download-memories
python download-creation.py -d ../../../translation-memories/po -t ../../../translation-memories/tmx
cd ../search
python index-creation.py -d ../../../translation-memories/po

# Notify completion
cd $PROGRAMS
pwd
python compare-sets.py -s $PROD_DIR -t $INTERMEDIATE_PO > report.txt
ls report.txt -l
cat report.txt | mail -s "Recursos updated" "jmas@softcatala.org" 



