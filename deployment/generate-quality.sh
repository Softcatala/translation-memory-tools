#!/bin/bash
root="$1"
lt_output=$root/tm-git/src/output/quality
location=$root/tm-git/src/output/individual_pos

# Delete output dir and files
mkdir -p $lt_output
echo Created quality directory: $lt_output

cd $root/tm-git/src/
python generate-quality-reports.py -s "$location"

