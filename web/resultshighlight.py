#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2014 Jordi Mas i Hernandez <jmas@softcatala.org>
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

from cleanstring import CleanString


class HighlightFragment:
    '''
            Stores a highlighted fragment

            Sample: un<b class = 'match term1'>sel</b>ect all            
                html_start: <b class = 'match term1'>
                text: sel
                html_end: </b>
        '''
    
    def __init__(self):
        self.html_start = ''
        self.text = ''
        self.html_end = ''

    def __str__(self):
        text = 'HighlightFragment. html_start: {0}, text: {1}, html_end: {2}'
        return text.format(self.html_start, self.text, self.html_end)


class ResultsHighlight:
    '''
        Source string: Unselec_t All        
        Clean string: unselect all
        Search: Sel* on the clean string
        Highlighted: un<b class = 'match term1'>sel</b>ect all        
    
        Algorithm:

        1. Create a list of fragments strings based on the 'clean string' to be 
           highlighted sorted by order of appearance

        2. Loop the 'source string'
            2.1 Convert to clean until we have a fragment of the length of the 
                the first to be matched in the list of fragments
            2.2 If there is a match, port the highlighted part
            2.3 Continue parsing the string

    '''

    @staticmethod
    def _read_fragment(clean_highlighted):
        '''
            <b class = 'match term1'>sel</b>            
            where 
                   'size' is the total size of the read string
                   'fragment' is the highlighted text (sel)
                   'html' (<b class = 'match term1'>)
        '''

        #print "clean_highlighted:" + clean_highlighted
        cnt = len(clean_highlighted)
        i = 0

        fragment = HighlightFragment()
       
        # Look for the HTML fragment to end <b class = 'match term1'> 
        while i < cnt and clean_highlighted[i] != '>':
                i = i + 1
                continue

        i = i + 1
        fragment.html_start = clean_highlighted[:i]
        start_pos = i
     
        # Look for the text fragment
        while i < cnt and clean_highlighted[i] != '<':
                i = i + 1
                continue

        fragment.text = clean_highlighted[start_pos:i]
        start_pos = i

        # Look for the HTML close tag </b> 
        while i < cnt and clean_highlighted[i] != '>':
                i = i + 1
                continue

        i = i + 1        
        fragment.html_end = clean_highlighted[start_pos:i]
        size = i
        return size, fragment

    @staticmethod
    def _read_fragments(clean_highlighted):
        '''
            Create a list of fragments strings based on the 'clean string' to
            be highlighted sorted by order of appearance
        '''

        cnt = len(clean_highlighted)
        i = 0
        fragments = []
        while i < cnt:
            if (clean_highlighted[i] == '<'):
                size, fragment = ResultsHighlight._read_fragment(clean_highlighted[i:])
                i += size
                fragments.append(fragment)
            else:
                i = i + 1

        return fragments

    @staticmethod
    def _get_source_matched_chars(source, text): 
        ''' 
            We need to find out how many chars from the source string
            were necessary to get the clean fragment

            Example: source: '_Sel' and clean:'sel'
        '''
        cnt = len(source)
        i = 0
        while i < cnt:
            i += 1
            clean_source = CleanString.get(source[:i])
            if text == clean_source:
                return i
             

    @staticmethod
    def _get_clean_fragment_match(source, fragment):        
        clean_source = CleanString.get(source)

        if fragment.text == clean_source[:len(fragment.text)]:
            matches = True
            size = ResultsHighlight._get_source_matched_chars(source, fragment.text)
            text = '{0}{1}{2}'.format(fragment.html_start, source[:size], fragment.html_end)
        else:
            matches = False
            size = 0
            text = None

        #print 'matches {0}, size {1}, text {2} ({3})'.format(matches, size, text, source)
        return matches, size, text
        
    @staticmethod
    def get(source, clean, clean_highlighted):
        fragments = ResultsHighlight._read_fragments(clean_highlighted)
        #print "source:" + source
        #print "clean:" + clean
        #print "clean_highlighted:" + clean_highlighted
        
        #print "Fragments"      
        #for fragment in fragments:
            #print fragment
        
        '''
        2. Loop the 'source string'
            2.1 Convert to clean until we have a fragment of the length of the 
                the first to be matched in the list of fragments
            2.2 If there is a match, port the highlighted part
            2.3 Continue parsing the string
        '''
        
        fragment_idx = 0
        cnt = len(source)
        i = 0
        result = ''
        
        while i < cnt:
            if fragment_idx < len(fragments):
                size = len(fragments[fragment_idx].text)
            else:
                size = 0

            if size > 0:
                matches, size, text = ResultsHighlight._get_clean_fragment_match(source[i:], fragments[fragment_idx])
                if matches:
                    fragment_idx += 1
                    i += size
                    result += text
                    continue

            clean_char = CleanString.get(source[i])

            if len(clean_char) > 0:
                result += source[i]

            i = i + 1

        #print "result:" + result
        return result
