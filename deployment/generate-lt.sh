#!/bin/bash

root="$1"
lt_output=$root/tm-git/src/lt
tike_path=/home/jmas/tika
lt_path=/home/jmas/languagetool
lt_log=$lt_output/excluded-lines.log 
langcode=ca-ES
disabledRules="-d MORFOLOGIK_RULE_CA_ES,WHITESPACE_RULE,UPPERCASE_SENTENCE_START,CAMI_DE"
enabledRules="-e EXIGEIX_PLURALS_S"
lt_opt="-u -b -c utf-8 -l $langcode $disabledRules $enabledRules"

# Try to download most recent LT version
yesterday=`date -d "yesterday 13:00 " '+%Y%m%d'`
lt_file=LanguageTool-$yesterday-snapshot.zip
lt_url="https://languagetool.org/download/snapshots/$lt_file"
wget -q $lt_url
if [[ $? -eq 0 ]]; then
    echo downloaded $lt_url
    rm $lt_path -r -f
    mkdir $lt_path
    #Skip the first directory on the zip file (e.g. /LanguageTool-3.0-SNAPSHOT)
    unzip -d "$lt_path" "$lt_file" && f=("$lt_path"/*) && mv "$lt_path"/*/* "$lt_path" && rmdir "${f[@]}"
    rm -f $lt_file
fi

# Delete output dir and files
rm -r -f $lt_log
rm -r -f $lt_output
mkdir $lt_output

cd $root/tm-git/src/terminology
cd tots-tm

# Run LT over all the files
for file in *.po; do
    echo "Executing LT on: " $file
    # Conversion from PO to HTML
    msgattrib --no-obsolete --no-fuzzy --translated $file > $file-filtrat.po
    po2txt $file-filtrat.po > $file.html
    sed -i 's/\\[rtn]/ /g' $file.html
    rm $file-filtrat.po

    # Conversion from HTML to TXT
    java -Dfile.encoding=UTF-8 -jar $tike_path/tika-app-1.7.jar -t "$file.html"  > "$file.txt"
    sed -i 's/[_&~]//g' $file.txt # remove accelerators
    
    # Exclude some patterns from LT analysis
    echo "*******************************************" >> $lt_log 
    echo "** Excluded lines from $file"                >> $lt_log
    echo "*******************************************" >> $lt_log
    grep -E '^([^.]*,[^.]*){8,}$' $file.txt >> $lt_log #comma-separated word list
    sed -i -r 's/^([^.]*,[^.]*){8,}$//' $file.txt
    
    # Run LT
    java -Dfile.encoding=UTF-8 -jar $lt_path/languagetool-commandline.jar $lt_opt "$file.txt" > "$file-results.txt"
    
    perl $root/tm-git/deployment/results-to-html.pl <"$file-results.txt" >"$lt_output/$file-lt.html"
    sed -i 's/\t/ /g' "$lt_output/$file-lt.html" #replace tabs with whitespace for better presentation
    
done


