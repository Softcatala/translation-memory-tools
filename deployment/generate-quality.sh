#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status

echo Generate Quality
root="$1"
lt_output=$root/tm-git/src/output/quality
location=$root/tm-git/src/output/individual_pos

mkdir -p $lt_output
echo Created quality directory: $lt_output

cd $root/tm-git/src/
python generate_quality_reports.py -s "$location"
cat generate_quality_reports-error.log >> applications-error.log
