#!/usr/bin/env python
import argparse
import sys
import codecs
if sys.version_info[0] == 2:
  from itertools import izip
else:
  izip = zip
from collections import defaultdict as dd
import re
import os.path
import gzip
import tempfile
import shutil
import atexit

# Use word_tokenize to split raw text into words
from string import punctuation

import nltk
from nltk.tokenize import word_tokenize

scriptdir = os.path.dirname(os.path.abspath(__file__))

reader = codecs.getreader('utf8')
writer = codecs.getwriter('utf8')

def prepfile(fh, code):
  if type(fh) is str:
    fh = open(fh, code)
  ret = gzip.open(fh.name, code if code.endswith("t") else code+"t") if fh.name.endswith(".gz") else fh
  if sys.version_info[0] == 2:
    if code.startswith('r'):
      ret = reader(fh)
    elif code.startswith('w'):
      ret = writer(fh)
    else:
      sys.stderr.write("I didn't understand code "+code+"\n")
      sys.exit(1)
  return ret

def addonoffarg(parser, arg, dest=None, default=True, help="TODO"):
  ''' add the switches --arg and --no-arg that set parser.arg to true/false, respectively'''
  group = parser.add_mutually_exclusive_group()
  dest = arg if dest is None else dest
  group.add_argument('--%s' % arg, dest=dest, action='store_true', default=default, help=help)
  group.add_argument('--no-%s' % arg, dest=dest, action='store_false', default=default, help="See --%s" % arg)

def is_not_empty(s):
  return s and s.strip()

def contain_letter(s):
  return s and re.search('[a-zA-Z]', s)

class LimerickDetector:

    def __init__(self):
        """
        Initializes the object to have a pronunciation dictionary available
        """
        self._pronunciations = nltk.corpus.cmudict.dict()
        

    def apostrophe_tokenize(self, sentence):
        s = re.sub(ur"[^\w\d'\s]+",'',sentence)       #strip all punctuations except apostrophe
        return s.split()

    def guess_syllables(self, word):
        count = 0
        vowel_list = ["a", "e", "i", "o", "u"]
        for i in range(len(word)):
          if word[i].lower() in vowel_list:
            count += 1
            is_consonant = False
          elif word[i].lower() == "y" and is_consonant:
            count += 1
          else:
            is_consonant = True
        return count
  

    def num_syllables(self, word):
        """
        Returns the number of syllables in a word.  If there's more than one
        pronunciation, take the shorter one.  If there is no entry in the
        dictionary, return 1.
        """

        # TODO: provide an implementation!
        if not is_not_empty(word):
          return 0
        if self._pronunciations.has_key(word.lower()):
          shortest = 1000
          pronunciation_list = self._pronunciations[word.lower()]
          for element in pronunciation_list:
            count = 0
            for x in element:
              if x[-1].isdigit():             #vowel ends with digit 
                count += 1
            if count < shortest:
              shortest = count
          return shortest if shortest > 0 else 1
        else:
          return 1

    def rhymes(self, a, b):
        """
        Returns True if two words (represented as lower-case strings) rhyme,
        False otherwise.
        """

        # TODO: provide an implementation!
        if self._pronunciations.has_key(a.lower()) and self._pronunciations.has_key(b.lower()):
          #normalize word a
          a_original_list = self._pronunciations[a.lower()]
          a_list = []
          for element in a_original_list:
            i = 0
            new_element = []
            for x in element:
              if x[-1].isdigit():
                new_element = element[i:]
                break
              else:
                i += 1
            a_list.append(new_element)   
          #normalize word b
          b_original_list = self._pronunciations[b.lower()]
          b_list = []
          for element in b_original_list:
            i = 0
            new_element = []
            for x in element:
              if x[-1].isdigit():
                new_element = element[i:]
                break
              else:
                i += 1
            b_list.append(new_element)  
          #check rhyme after normalizing based on len
          for elem_a in a_list:
            for elem_b in b_list:
              if len(elem_a) == len(elem_b):          #a and b must have exact same elements in list
                result = True
                for i in range(len(elem_a)):
                  if elem_a[i] != elem_b[i]:
                    result = False
                    break
                if result == True:
                  return True
                else:
                  continue
              else:
                if len(elem_a) == 0 or len(elem_b) == 0:
                  return True
                result = True
                end = -1 - len(elem_a) if len(elem_a) < len(elem_b) else -1 - len(elem_b)
                for i in range(-1, end, -1):
                  if elem_a[i] != elem_b[i]:
                    result = False
                    break
                if result == True:
                  return True
                else:
                  continue     
          return False        #all comparisions fail   
        else:  
          return False


    


    def is_limerick(self, text):
        """
        Takes text where lines are separated by newline characters.  Returns
        True if the text is a limerick, False otherwise.

        A limerick is defined as a poem with the form AABBA, where the A lines
        rhyme with each other, the B lines rhyme with each other, and the A lines do not
        rhyme with the B lines.


        Additionally, the following syllable constraints should be observed:
          * No two A lines should differ in their number of syllables by more than two.
          * The B lines should differ in their number of syllables by no more than two.
          * Each of the B lines should have fewer syllables than each of the A lines.
          * No line should have fewer than 4 syllables

        (English professors may disagree with this definition, but that's what
        we're using here.)


        """
        # TODO: provide an implementation!
        text_list = text.splitlines()
        text_list = filter(is_not_empty, text_list)
        if len(text_list) != 5:
          return False
        a1 = nltk.word_tokenize(text_list[0])
        a1 = filter(contain_letter, a1)
        a2 = nltk.word_tokenize(text_list[1])
        a2 = filter(contain_letter, a2)
        b1 = nltk.word_tokenize(text_list[2])
        b1 = filter(contain_letter, b1)
        b2 = nltk.word_tokenize(text_list[3])
        b2 = filter(contain_letter, b2)
        a3 = nltk.word_tokenize(text_list[4])
        a3 = filter(contain_letter, a3)
        #calculate syllables in each sentence
        a1_syllables = a2_syllables = b1_syllables = b2_syllables = a3_syllables = 0
        for x in a1:
          a1_syllables += self.num_syllables(x)
        for x in a2:
          a2_syllables += self.num_syllables(x)
        for x in b1:
          b1_syllables += self.num_syllables(x)
        for x in b2:
          b2_syllables += self.num_syllables(x)
        for x in a3:
          a3_syllables += self.num_syllables(x)
        #check syllable constrains
        if a1_syllables < 4 or a2_syllables < 4 \
            or b1_syllables < 4 or b2_syllables < 4 \
            or a3_syllables < 4:
              return False
        if abs(b1_syllables - b2_syllables) > 2:
          return False
        if abs(a1_syllables - a2_syllables) > 2 \
            or abs(a1_syllables - a3_syllables) > 2 \
            or abs(a2_syllables - a3_syllables) > 2:
              return False
        min_a_syllables = min(a1_syllables, a2_syllables, a3_syllables)
        if b1_syllables >= min_a_syllables or b2_syllables >= min_a_syllables:
          return False
        #check rhyme
        if self.rhymes(a1[-1], a2[-1]) == False \
          or self.rhymes(a1[-1], a3[-1]) == False \
          or self.rhymes(a2[-1], a3[-1]) == False:
            return False
        if self.rhymes(b1[-1], b2[-1]) == False:
          return False
        if self.rhymes(a1[-1], b1[-1]) or self.rhymes(a1[-1], b2[-1]):
          return False

        return True

# The code below should not need to be modified
def main():
  parser = argparse.ArgumentParser(description="limerick detector. Given a file containing a poem, indicate whether that poem is a limerick or not",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  addonoffarg(parser, 'debug', help="debug mode", default=False)
  parser.add_argument("--infile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input file")
  parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file")




  try:
    args = parser.parse_args()
  except IOError as msg:
    parser.error(str(msg))

  infile = prepfile(args.infile, 'r')
  outfile = prepfile(args.outfile, 'w')

  ld = LimerickDetector()
  lines = ''.join(infile.readlines())
  outfile.write("{}\n-----------\n{}\n".format(lines.strip(), ld.is_limerick(lines)))

if __name__ == '__main__':
  main()
