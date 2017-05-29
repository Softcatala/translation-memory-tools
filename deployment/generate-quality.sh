#!/bin/bash

root="$1"
lt_output=$root/tm-git/src/output/quality
lt_log=$lt_output/excluded-lines.log 
location=$root/tm-git/src/output/individual_pos
cnt=0

# Delete output dir and files
rm -r -f $lt_log
mkdir -p $lt_output

cd $location
# Every project has its own subdirectory
for project_dir in */; do
    project_dir=$location/$project_dir
    echo "project_dir:" $project_dir

    has_files=`find "$project_dir" -type f -name "*.po"| wc -l`
    if [ $has_files -eq 0 ]; then
        echo "Skipping quality report since no po files"
        continue
    fi

    echo "cnt: " $cnt
    if [ $cnt == 4 ]; then
        echo "waiting"
        wait
        cnt=0
    fi

    cd $root/tm-git/src/
    python generate-quality-reports.py -s "$project_dir" &
    cnt=$((cnt+1))   
done
wait

