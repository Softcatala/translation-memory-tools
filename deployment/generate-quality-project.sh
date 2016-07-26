#!/bin/bash

SECONDS=0
root="$1"
lt_output=$root/tm-git/src/output/quality
lt_html=$root/tm-git/src/quality/lt
tike_path=/home/jmas/tika
lt_log=$lt_output/excluded-lines.log 
langcode=ca-ES
disabledRules="WHITESPACE_RULE,UPPERCASE_SENTENCE_START,CAMI_DE"
enabledRules="EXIGEIX_PLURALS_S"
pology=$root/tm-git/src/quality/pology
project_dir="$2"

echo "project_dir_project:" $project_dir
# Run LT over all the files
report_file="${project_dir::-1}.html"

cat $lt_html/header.html > "$lt_output/$report_file"
find "$project_dir" -type f -name '*.po' -print0 | sort -z | while IFS= read -r -d '' file; do

    source /home/jmas/web/python3-env/bin/activate # Specific to SC machine cfg
    echo "Executing LT on: " "$file"
    # Conversion from PO to HTML
    msgattrib --no-obsolete --no-fuzzy --translated "$file" > "$file-filtrat.po"
    po2txt "$file-filtrat.po" > "$file.txt"
    sed -i 's/\\[rtn]/ /g' "$file.txt"

    sed -i 's/[_&~]//g' "$file.txt" # remove accelerators
 
    if [ ! -s  "$file.txt" ]; then
        echo "No translations in file" "$file"
        rm "$file-filtrat.po"
        continue
    fi

    # Exclude some patterns from LT analysis
    echo "*******************************************" >> $lt_log 
    echo "** Excluded lines from $file"                >> $lt_log
    echo "*******************************************" >> $lt_log
    grep -E '^([^.]*,[^.]*){8,}$' "$file.txt" >> $lt_log #comma-separated word list
    sed -i -r 's/^([^.]*,[^.]*){8,}$//' "$file.txt"
    
    # Run LT
    curl --data "language=$langcode" --data "enabled=$enabledRules" --data "disabled=$disabledRules" --data-urlencode "text@$file.txt" http://localhost:7001 > "$file.xml" 2>/dev/null
    
    python $lt_html/lt-results-to-html.py -i "$file.xml" -o "$file-report.html"
    sed -i 's/\t/ /g' "$file-report.html" #replace tabs with whitespace for better presentation
    cat "$file-report.html" >> "$lt_output/$report_file"

    # Execute pology
    deactivate  # Specific to SC machine cfg
    echo "Executing posieve on: " "$file"
    posieve set-header -sfield:'Language:ca' -screate "$file-filtrat.po"
    posieve --skip-obsolete --coloring-type=html check-rules -s rfile:$pology/upstream/punctuation.rules -s rfile:$pology/upstream/false-friends.rules -s rfile:$pology/upstream/keys.rules -s rfile:$pology/catalan-pology-rules/date-format.rules -s rfile:$pology/catalan-pology-rules/terminology-sc.rules -s rfile:$pology/catalan-pology-rules/iso_639.rules -s rfile:$pology/catalan-pology-rules/acronyms.rules "$file-filtrat.po" > "$file-pology.html"

    echo "<h2>Informe d'errades del Pology</h2><br/>" >> "$lt_output/$report_file"
    if [ -s "$file-pology.html" ] ; then
        cat "$file-pology.html" >> "$lt_output/$report_file"
    else
        echo "El Pology no detectat cap error." >> "$lt_output/$report_file"
    fi
    source /home/jmas/web/python3-env/bin/activate # Specific to SC machine cfg

    rm "$file-filtrat.po"
    rm "$file-pology.html"
    rm "$file-report.html"
    rm "$file.xml"
    rm "$file.txt"
    
done
echo "<p><i>Informe generat el `date +%Y-%m-%d`</i></p>" >> "$lt_output/$report_file"
cat $lt_html/footer.html >> "$lt_output/$report_file"

duration=$SECONDS
echo "Generated quality for $project_dir: $(($duration / 60))m $(($duration % 60))s."
