#!/bin/bash
ROOT=/home/jmas/
INTERMEDIATE_PO=/home/jmas/translation-memories/po
INTERMEDIATE_TMX=/home/jmas/translation-memories/tmx
PROGRAMS=/home/jmas/tm-git/src
PROD_DIR=/var/www/recursos.softcatala.org/
BACKUP_DIR=/home/jmas/previous

# Catalan locale does not support thounsand separator
export LC_ALL=ast_ES.utf-8

# Copy existing PO files
rm -r -f $BACKUP_DIR
mkdir $BACKUP_DIR
cd $BACKUP_DIR
cp $INTERMEDIATE_PO/* $BACKUP_DIR

# Download new translation files
cd $PROGRAMS
rm -f *.po
rm -f *.tmx
rm -f *.log
python builder.py

# Build aggregated memories
cd $INTERMEDIATE_PO/
python $PROGRAMS/builder.py -s $PROGRAMS/projects.json --all
python $PROGRAMS/builder.py -s $PROGRAMS/projects.json --softcatala
cp *.tmx $INTERMEDIATE_TMX/

cd $PROGRAMS
# Copy only new PO files
for filename in *.po
  do
    # If file exists and size is greater than 200 bytes
    if [ -e  $filename ]
      then
        fsize=$(du -b "$filename" | cut -f 1)
        if [ $fsize -ge 200 ];
          then
	    if ! diff -q $filename $INTERMEDIATE_PO/$filename > /dev/null
	      then
	        echo Copying $filename
                cp $filename $INTERMEDIATE_PO/$filename
            fi
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

# Update download file & index
cd /home/jmas/tm-git/web/download-memories
python download-creation.py -d $INTERMEDIATE_PO -t $INTERMEDIATE_TMX
cd ../search
python index-creation.py -d $INTERMEDIATE_PO

# Notify completion
cd $PROGRAMS
pwd
python compare-sets.py -s  $BACKUP_DIR -t $INTERMEDIATE_PO > report.txt
ls report.txt -l
cat report.txt | mail -s "Recursos updated" "jmas@softcatala.org" 



