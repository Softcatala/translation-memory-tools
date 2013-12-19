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
import datetime
import cgi
from optparse import OptionParser
from corpus import Corpus

src_directory = None
html_comment = ''
hmtl_file = None

class Translation:
    def __init__(self):
        self.translation = ''
        self.frequency = 0
        self.percentage = 0  # Percentage of frequency across all options

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

    f = open('glossary.txt', 'w')
    terms = sorted(tfxdf, key=tfxdf.get, reverse=True)

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

def create_html_glossary_for_all_projects(documents, source_words, tfxdf, terms_recull, strings, strings_selected):

    global html_file

    terms = sorted(tfxdf, key=tfxdf.get, reverse=True)

    f = open(html_file,'w')

    f.write(u'<html><head>\n')
    f.write(u'<meta http-equiv="content-type" content="text/html; charset=UTF-8">')
    html = ''

    html += u'<p><b>Comentaris</b></p><ul>'
    html += u'<li>Glossari generat computacionalment al final del mateix hi ha dades sobre la generació.</li>'
    html += u'<li>La columna opcions considerades indica quines altres traduccions apareixen per aquest terme i s\'han considerat.</li>'
    html += u'<li>La columna català és l\'opció més comuna.</li>'
    html += u'<li>Usada indica el % d\'ús respecte a altres opcions i coincidències els cops que s\'ha trobat.</li>'
    html += u'<li>(r) indica el terme es troba a l\'últim Recull de termes publicat.</li>'    
    html += u'</ul>'
    
    html += u'<table border="1" cellpadding="5px" cellspacing="5px" style="border-collapse:collapse;">\r'
    html += u'<tr>\r'
    html += u'<th>#</th>\r'
    html += u'<th>Anglès</th>\r'
    html += u'<th>Català</th>\r'
    html += u'<th>Opcions considerades</th>\r'
    html += '</tr>\r'
    f.write(html.encode('utf-8'))

    item = 0
    first_50 = 0
    first_100 = 0
    first_500 = 0
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

        if item < 50 and len(inrecull) > 0:
            first_50 += 1
        
        if item < 100 and len(inrecull) > 0:
            first_100 += 1

        if item < 500 and len(inrecull) > 0:
            first_500 += 1

        if item >= 1000:
            break

    f.write('</table>\n')

    global html_comment

    html = u'<p>Data de generació: {0}</p>'.format(datetime.date.today().strftime("%d/%m/%Y"))
    html += '<p>Cadenes analitzades: {0}</p>'.format(strings) 
    html += '<p>Cadenes seleccionades: {0} - {1}%</p>'.format(strings_selected, 100 * strings_selected / strings) 
    html += u'<p>Termes únics totals selecionats: {0}</p>'.format(len(source_words))
    html += '<p>Dels 50 primers termes quants eren al Recull: {0}% ({1})</p>'.format(first_50 * 100 / 50, first_50)
    html += '<p>Dels 100 primers termes quants eren al Recull: {0}% ({1})</p>'.format(first_100 * 100 / 100, first_100)       
    html += '<p>Dels 500 primers termes quants eren al Recull: {0}% ({1})</p>'.format(first_500 * 100 / 500, first_500) 

    if len(html_comment) > 0:
        u = unicode(html_comment, "UTF-8") # utf-8 is the system encoding
        html += u"Comentari de generació: " + u 

    f.write(html.encode('utf-8'))
  
    f.write('</head></html>\n')
    f.close()

def read_recull():

    pofile = polib.pofile('recull/recull-glossary.po')
        
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

    f.close()
      
    # Use cases
    #  1. Calculate TF -> need term, frequency in the document
    #  2. Calculate IDF -> need n of documents, documents containing the term
    #  3. Search all words 
    #
    # Values 
    
def process_projects():

    corpus = Corpus(src_directory)
    corpus.process()

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

    for source_word in corpus.source_words:
        frequency = 0
        documents_appear = 0
        for document_key_filename in corpus.documents.keys():
            if source_word in corpus.documents[document_key_filename]: # Word not in the file
                documents_appear += 1
                terms = corpus.documents[document_key_filename][source_word]
                frequency += len(terms)

        tf[source_word] = frequency
        _idf = math.log(len(corpus.documents) / documents_appear)
        idf[source_word] = _idf
        df[source_word] = documents_appear
        tfxidf[source_word] = frequency * _idf
        tfxdf[source_word] = frequency * documents_appear
        #print 'Source word {0} - {1} - {2}'.format(source_word.encode('utf-8'), frequency, _idf)

    terms_recull = read_recull()

    calculate_most_frequent(corpus.source_words, tf, df, tfxdf, terms_recull)
    #create_glossary_for_all_projects(documents, source_words, tfxdf, terms_recull)
    create_html_glossary_for_all_projects(corpus.documents, corpus.source_words, tfxdf, terms_recull, 
                                          corpus.strings, corpus.strings_selected)

    # tf x idf
    f = open('td-idx.txt','w')        
    terms = sorted(tfxidf, key=tfxidf.get,reverse=True)

    for term in terms:
        f.write('{0} - {1} (tf: {2}, idf: {3})\n'.format(term.encode('utf-8'), tfxidf[term],
               tf[term], idf[term]))
    f.close()
        
def read_parameters():

    global src_directory
    global html_comment
    global html_file
   
    parser = OptionParser()

    parser.add_option("-s", "--srcdir",
                      action="store", type="string", dest="src_directory",
                      #default = "/home/jordi/sc/other/src/pos/",
                      default = "sc-tm-pos/",
                      help="Directory to find the PO files")

    parser.add_option("-c", "--comment",
                      action="store", type="string", dest="html_comment",
                      default = "",
                      help="HTML comment to add")

    parser.add_option("-t", "--html-file",
                      action="store", type="string", dest="html_file",
                      default = "glossary.html",
                      help="HTML file to export")

    (options, args) = parser.parse_args()
    src_directory = options.src_directory
    html_comment = options.html_comment
    html_file = options.html_file

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

