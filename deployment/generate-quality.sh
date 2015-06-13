#!/bin/bash

root="$1"
lt_output=$root/tm-git/quality
lt_html=$root/tm-git/src/quality/lt
tike_path=/home/jmas/tika
lt_path=/home/jmas/languagetool
lt_log=$lt_output/excluded-lines.log 
langcode=ca-ES
disabledRules="WHITESPACE_RULE,UPPERCASE_SENTENCE_START,CAMI_DE"
enabledRules="EXIGEIX_PLURALS_S"
pology=$root/tm-git/src/quality/pology
cnt=0

# Delete output dir and files
rm -r -f $lt_log
mkdir -p $lt_output

cd $root/tm-git/src/builder/output

# Every project has its own subdirectory
for project_dir in */; do
    echo "project_dir:" $project_dir
    echo "cnt: " $cnt
    if [ $cnt == 6 ]; then
        echo "waiting"
        wait
        $cnt=0
    fi

    bash $root/tm-git/deployment/generate-quality-project.sh $root $project_dir &
    cnt=$((cnt+1))   
done
wait

