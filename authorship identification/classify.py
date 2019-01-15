#!/usr/bin/env python
from collections import defaultdict
from csv import DictReader, DictWriter

import nltk
import codecs
import sys
from nltk.corpus import wordnet as wn
from nltk.tokenize import TreebankWordTokenizer
from nltk.util import ngrams


kTOKENIZER = TreebankWordTokenizer()
pronunciations_dict = nltk.corpus.cmudict.dict()

def morphy_stem(word):
    """
    Simple stemmer
    """
    stem = wn.morphy(word)
    if stem:
        return stem.lower()
    else:
        return word.lower()

def is_not_empty(s):
    return s and s.strip()

def num_syllables(word):
        """
        Returns the number of syllables in a word.  If there's more than one
        pronunciation, take the shorter one.  If there is no entry in the
        dictionary, return 1.
        """

        # TODO: provide an implementation!
        if not is_not_empty(word):
          return 0
        if pronunciations_dict.has_key(word.lower()):
          shortest = 1000
          pronunciation_list = pronunciations_dict[word.lower()]
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


class FeatureExtractor:
    def __init__(self):
        """
        You may want to add code here
        """
        None

    def features(self, text):
        d = defaultdict(int)
        text_list = kTOKENIZER.tokenize(text)
        sum_len = 0
        text_len = len(text_list)
        d[len(text)] += 1
        d[text[-1]] += 1
        for i in range(text_len):
            # d[morphy_stem(text_list[i])] += 1
            d[num_syllables(text_list[i])] += i + 1
            # d[text_list[i]] += i  # words before
            # d[text_list[i]] += text_len - i - 1 # words after
            # sum_len += len(text_list[i])*(i+1)

        # d[sum_len] += 1
        # ngram = ngrams(text, 4)
        # for i in ngram:
        #     d[i] += 1

        # ngram = ngrams(text_list, 3)
        # for i in ngram:
        #     d[i] += 1

        return d

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

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--trainfile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input train file")
    parser.add_argument("--testfile", "-t", nargs='?', type=argparse.FileType('r'), default=None, help="input test file")
    parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file")
    parser.add_argument('--subsample', type=float, default=1.0,
                        help='subsample this fraction of total')
    args = parser.parse_args()
    trainfile = prepfile(args.trainfile, 'r')
    if args.testfile is not None:
        testfile = prepfile(args.testfile, 'r')
    else:
        testfile = None
    outfile = prepfile(args.outfile, 'w')

    # Create feature extractor (you may want to modify this)
    fe = FeatureExtractor()
    
    # Read in training data
    train = DictReader(trainfile, delimiter='\t')
    
    # Split off dev section
    dev_train = []
    dev_test = []
    full_train = []

    for ii in train:
        if args.subsample < 1.0 and int(ii['id']) % 100 > 100 * args.subsample:
            continue
        feat = fe.features(ii['text'])
        if int(ii['id']) % 5 == 0:
            dev_test.append((feat, ii['cat']))
        else:
            dev_train.append((feat, ii['cat']))
        full_train.append((feat, ii['cat']))

    # Train a classifier
    sys.stderr.write("Training classifier ...\n")
    classifier = nltk.classify.NaiveBayesClassifier.train(dev_train)

    right = 0
    total = len(dev_test)
    for ii in dev_test:
        prediction = classifier.classify(ii[0])
        if prediction == ii[1]:
            right += 1
    sys.stderr.write("Accuracy on dev: %f\n" % (float(right) / float(total)))

    if testfile is None:
        sys.stderr.write("No test file passed; stopping.\n")
    else:
        # Retrain on all data
        classifier = nltk.classify.NaiveBayesClassifier.train(dev_train + dev_test)

        # Read in test section
        test = {}
        for ii in DictReader(testfile, delimiter='\t'):
            test[ii['id']] = classifier.classify(fe.features(ii['text']))

        # Write predictions
        o = DictWriter(outfile, ['id', 'pred'])
        o.writeheader()
        for ii in sorted(test):
            o.writerow({'id': ii, 'pred': test[ii]})
