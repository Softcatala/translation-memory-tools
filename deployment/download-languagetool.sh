#!/bin/bash


# Try to download most recent LT version
# Not used for now since it is running as a service
yesterday=`date -d "yesterday 13:00 " '+%Y%m%d'`
lt_file=LanguageTool-$yesterday-snapshot.zip
lt_url="https://languagetool.org/download/snapshots/$lt_file"
lt_path=/home/jmas/languagetool
wget -q $lt_url
if [[ $? -eq 0 ]]; then
    echo downloaded $lt_url
    sudo supervisorctl stop language_tool
    rm $lt_path -r -f
    mkdir $lt_path
    #Skip the first directory on the zip file (e.g. /LanguageTool-3.0-SNAPSHOT)
    unzip -d "$lt_path" "$lt_file" && f=("$lt_path"/*) && mv "$lt_path"/*/* "$lt_path" && rmdir "${f[@]}"
    rm -f $lt_file
    sudo supervisorctl start language_tool
fi


