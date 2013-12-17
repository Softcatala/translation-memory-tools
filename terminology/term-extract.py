#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2013 Jordi Mas i Hernandez <jmas@softcatala.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import sys
sys.path.append('../src/')

import time
import math
import polib
import cgi
from findfiles import FindFiles
from optparse import OptionParser

src_directory = None

class Translation:
    def __init__(self):
        self.translation = ''
        self.frequency = 0
        self.percentage = 0  # Percentage of frequency across all options

def dump_documents(documents):

    for document_key_filename in documents.keys():
        print document_key_filename
        for terms in documents[document_key_filename].keys():
            print "  s({0}):{1}".format(len(documents[document_key_filename][terms]), terms.encode('utf-8'))
            for translation in documents[document_key_filename][terms]:
                print "     t:" + translation.encode('utf-8')

def create_translations_for_word_sorted_by_frequency(documents, term):

    translations = {} # key: english keyword -> value: list of translation objects
    for document_key_filename in documents.keys():
        if term not in documents[document_key_filename]:
            continue

        for translated in documents[document_key_filename][term]:
            #print "     t:" +m translated.encode('utf-8')
            if term in translations:
                translation_list = translations[term]
            else:
                translation_list = []

            found = False
            for i in range(0, len(translation_list)):
                if translation_list[i].translation == translated:
                    translation_obj_item = translation_list[i]
                    translation_obj_item.frequency += 1
                    translation_list[i] = translation_obj_item
                    found = True
                    break

            if found is False:
                translation_obj_item = Translation()
                translation_obj_item.translation = translated
                translation_obj_item.frequency = 1
                translation_list.append(translation_obj_item)

            translations[term] = translation_list
    
    for translation_obj_list in translations.values():

        translation_obj_list_sorted = sorted(translation_obj_list, key=lambda x: x.frequency, reverse=True)

        all_frequencies = 0

        for translation in translation_obj_list_sorted:
            all_frequencies += translation.frequency

        for translation in translation_obj_list_sorted:
            translation.percentage = translation.frequency * 100 / all_frequencies

    return translation_obj_list_sorted  

def create_glossary_for_all_projects(documents, source_words, tfxdf, terms_recull):

    f = open('glossary.txt','w')
    terms = sorted(tfxdf, key=tfxdf.get,reverse=True)

    item = 1
    for term in terms:
        if term in terms_recull.keys():
            inrecull = '- Recull'
        else:
            inrecull = ''

        f.write('{0} - {1} {2}\n'.format(item, term.encode('utf-8'),
                inrecull))
        item += 1

        translations = create_translations_for_word_sorted_by_frequency(documents, term)

        for translation in translations:
            f.write('  {0} - {1}% ({2})\n'.format(translation.translation.encode('utf-8'), 
                    translation.percentage, translation.frequency)) 
   
    f.close()

def create_html_glossary_for_all_projects(documents, source_words, tfxdf, terms_recull):

    terms = sorted(tfxdf, key=tfxdf.get, reverse=True)

    f = open('glossary.html','w')

    f.write(u'<html><head>\n')
    f.write(u'<meta http-equiv="content-type" content="text/html; charset=UTF-8">')

    html = u'<table border="1" cellpadding="5px" cellspacing="5px" style="border-collapse:collapse;">\r'
    html += u'<tr>\r'
    html += u'<th>#</th>\r'
    html += u'<th>Anglès</th>\r'
    html += u'<th>Català</th>\r'
    html += u'<th>Opcions considerades</th>\r'
    html += '</tr>\r'
    f.write(html.encode('utf-8'))

    item = 0
    for term in terms:
        if term in terms_recull.keys():
            inrecull = ' (r)'
        else:
            inrecull = ''

        item += 1

        translations = create_translations_for_word_sorted_by_frequency(documents, term)

        options = ''
        for translation in translations:
            options += u'<p>- {0} (usada {1}%, coincidències {2})</p>\n'.format(cgi.escape(translation.translation),
                        translation.percentage, translation.frequency)
    
        html = u"<tr>\r"
        html += u'<td>{0}</td>'.format(item)
        html += u'<td>{0}{1}</td>'.format(cgi.escape(term), inrecull)
        html += u'<td>{0}</td>'.format(cgi.escape(translations[0].translation))
        html += u'<td>{0}</td>'.format(options)
        html += u"</tr>\r"
        f.write(html.encode('utf-8'))
        
        if item >= 2000:
            break
   
    f.write('</head></html>\n')
    f.close()

def read_recull():

    pofile = polib.pofile('../source-pos/recull/recull.po')
        
    terms = {}
    for entry in pofile:
        terms[entry.msgid.lower()] = entry.msgstr.lower()

    return terms

def calculate_most_frequent(source_words, tf, df, tfxdf, terms_recull):

    # Most frequent
    f = open('most-frequent.txt','w')
    terms = sorted(tfxdf, key=tfxdf.get,reverse=True)

    item = 1
    first_50 = 0
    first_100 = 0
    for term in terms:
        if term in terms_recull.keys():
            inrecull = '- Recull'
        else:
            inrecull = ''
        f.write('{0} - {1} - {2} (tf: {3}, idf: {4}) {5}\n'.format(item, term.encode('utf-8'), tfxdf[term],
               tf[term], df[term], inrecull))
        item += 1
        if item < 50 and len(inrecull) > 0:
            first_50 += 1
        if item < 100 and len(inrecull) > 0:
            first_100 += 1

    print 'Source words {0}'.format(len(source_words))
    print '50 first words in recull: {0} - {1}%'.format(first_50, first_50 * 100 /50)
    print '100 first words in recull: {0} - {1}%'.format(first_100, first_50 * 100 /100)  
    f.close()

def clean_string(result):

    chars = {'_', '&', '~', # Accelarators
            ':', ',' # Punctuations
    }
  
    for c in chars:
        result = result.replace(c, '')
    
    result = result.lower()
    return result       

def process_projects():

    findFiles = FindFiles()

    # Use cases
    #  1. Calculate TF -> need term, frequency in the document
    #  2. Calculate IDF -> need n of documents, documents containing the term
    #  3. Search all words 
    #
    # Values 
    #
    # Option 1 (this)
    #  1. Dictionary key:document, value:(key: term src, value:list <trgs>)
  
    source_words = set()
    documents = {}
    files = 0
    for filename in findFiles.find(src_directory, '*.po'):
        print filename

        pofile = polib.pofile(filename)
        
        terms = {}
        for entry in pofile:
            # Only 1 word terms for now
            if len(entry.msgid.split()) > 1:
                continue

            msgid = clean_string(entry.msgid)
            msgstr = clean_string(entry.msgstr)

            # Single words without spaces that are very long
            if len(msgid) > 30:
                continue
           
            # Single chars provide no value
            if len(msgid) < 2:
                continue

            if not msgid in terms.keys():
                translations = []
            else:
                translations = terms[msgid]

            source_words.add(msgid)
            translations.append(msgstr)
            terms[msgid] = translations

    
        documents[filename] = terms
        files += 1
        #if files > 10:
        #    break
 
    #dump_documents(documents)

    # 
    # Processed
    #  
    #  1. term -> tf, idf, tfxidf

    # TF
    # Count the number of times each term occurs in each document and sum them all together; 
    # the number of times a term occurs in a document is called its term frequency.
    tf = {} # keyword -> frequency

    # IDF
    # It is obtained by dividing the total number of documents by the number of documents containing the term,
    idf = {}

    # TFxIDF
    # It is obtained by dividing the total number of documents by the number of documents containing the term,
    tfxidf = {}

    tfxdf = {}
    df = {}

    for source_word in source_words:
        frequency = 0
        documents_appear = 0
        for document_key_filename in documents.keys():
            if source_word in documents[document_key_filename]: # Word not in the file
                documents_appear += 1
                terms = documents[document_key_filename][source_word]
                frequency += len(terms)

        tf[source_word] = frequency
        _idf = math.log(len(documents) / documents_appear)
        idf[source_word] = _idf
        df[source_word] = documents_appear
        tfxidf[source_word] = frequency * _idf
        tfxdf[source_word] = frequency * documents_appear
        #print 'Source word {0} - {1} - {2}'.format(source_word.encode('utf-8'), frequency, _idf)

    terms_recull = read_recull()

    calculate_most_frequent(source_words, tf, df, tfxdf, terms_recull)
    #create_glossary_for_all_projects(documents, source_words, tfxdf, terms_recull)
    create_html_glossary_for_all_projects(documents, source_words, tfxdf, terms_recull)

    # tf x idf
    f = open('td-idx.txt','w')        
    terms = sorted(tfxidf, key=tfxidf.get,reverse=True)

    for term in terms:
        f.write('{0} - {1} (tf: {2}, idf: {3})\n'.format(term.encode('utf-8'), tfxidf[term],
               tf[term], idf[term]))
    f.close()
        
def read_parameters():

    global src_directory
   
    parser = OptionParser()

    parser.add_option("-s", "--srcdir",
                      action="store", type="string", dest="src_directory",
                      default = "pos/",
                      help="Directory to find the PO files")

    (options, args) = parser.parse_args()
    src_directory = options.src_directory
    

def main():
    
    print "Extracts terminology"
    print "Use --help for assistance"

    read_parameters()
    process_projects()
    return

    try:
        start_time = time.time()
        process_projects()
        end_time = time.time() - start_time
        print "time used to create the glossaries: " + str(end_time)

    except Exception as detail:
        print "Exception!"
        print detail
    

if __name__ == "__main__":
    main()

