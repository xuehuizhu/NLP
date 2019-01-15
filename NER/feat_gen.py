#!/bin/python
import codecs

first_name = []
last_name = []
english_stop = []
# location = []
cap = []
lower_list = []
internet = []

def preprocess_corpus(train_sents):
    """Use the sentences to do whatever preprocessing you think is suitable,
    such as counts, keeping track of rare features/words to remove, matches to lexicons,
    loading files, and so on. Avoid doing any of this in token2features, since
    that will be called on every token of every sentence.

    Of course, this is an optional function.

    Note that you can also call token2features here to aggregate feature counts, etc.
    """
    global first_name
    f = open("data/lexicon/firstname.5k", "r")
    first_name.extend(f.read().splitlines())
    f.close

    global last_name
    f = open("data/lexicon/lastname.5000", "r")
    last_name.extend(f.read().splitlines())
    f.close
    temp = []
    f = open("data/lexicon/people.family_name", "r")
    temp.extend(f.read().splitlines())
    f.close
    temp = [item.lower() for item in temp]
    last_name.append(temp)
    temp2 = []
    f = codecs.open("data/lexicon/people.person.lastnames", "r", encoding='utf-8')
    temp2.extend(f.read().splitlines())
    f.close
    temp2 = [item.lower() for item in temp2]
    last_name.append(temp2)


    global english_stop
    f = open("data/lexicon/english.stop", "r")
    english_stop.extend(f.read().splitlines())
    f.close

    global cap
    f = open("data/lexicon/cap.1000", "r")
    cap.extend(f.read().splitlines())
    f.close

    # global location
    # f = codecs.open("data/lexicon/location", "r", encoding='utf-8')
    # location.extend(f.read().splitlines())
    # f.close
    # location = [item.lower() for item in location]
    # temp = []
    # f = open("data/lexicon/location.country", "r")
    # temp.extend(f.read().splitlines())
    # f.close
    # temp = [item.lower() for item in temp]
    # location.append(temp)

    global lower_list
    f = open("data/lexicon/lower.5000", "r")
    lower_list.extend(f.read().splitlines())
    f.close

    global internet
    f = codecs.open("data/lexicon/internet.website", "r", encoding='utf-8')
    internet.extend(f.read().splitlines())
    f.close


def token2features(sent, i, add_neighs = True):
    """Compute the features of a token.

    All the features are boolean, i.e. they appear or they do not. For the token,
    you have to return a set of strings that represent the features that *fire*
    for the token. See the code below.

    The token is at position i, and the rest of the sentence is provided as well.
    Try to make this efficient, since it is called on every token.

    One thing to note is that it is only called once per token, i.e. we do not call
    this function in the inner loops of training. So if your training is slow, it's
    not because of how long it's taking to run this code. That said, if your number
    of features is quite large, that will cause slowdowns for sure.

    add_neighs is a parameter that allows us to use this function itself in order to
    recursively add the same features, as computed for the neighbors. Of course, we do
    not want to recurse on the neighbors again, and then it is set to False (see code).
    """
    ftrs = []
    # bias
    ftrs.append("BIAS")
    # position features
    if i == 0:
        ftrs.append("SENT_BEGIN")
    if i == len(sent)-1:
        ftrs.append("SENT_END")

    # the word itself
    word = unicode(sent[i])
    ftrs.append("WORD=" + word)
    ftrs.append("LCASE=" + word.lower())
    # some features of the word
    if word.isalnum():
        ftrs.append("IS_ALNUM")
    if word.isnumeric():
        ftrs.append("IS_NUMERIC")
    if word.isdigit():
        ftrs.append("IS_DIGIT")
    if word.isupper():
        ftrs.append("IS_UPPER")
    if word.islower():
        ftrs.append("IS_LOWER")
    if word.upper() in first_name:
        ftrs.append("IS_FIRSTNAME")
    if word.lower() in last_name:
        ftrs.append("IS_LASTNAME")
    if word in english_stop:
        ftrs.append("IS_ENGLISHSTOP")
    # if word in location:
    #     ftrs.append("IS_LOCATION")
    if word in cap:
        ftrs.append("IS_CAP")
    if word in lower_list:
        ftrs.append("IS_LOWERLIST")
    if word in internet:
        ftrs.append("IS_INTERNET")

    # previous/next word feats
    if add_neighs:
        if i > 0:
            for pf in token2features(sent, i-1, add_neighs = False):
                ftrs.append("PREV_" + pf)
        if i < len(sent)-1:
            for pf in token2features(sent, i+1, add_neighs = False):
                ftrs.append("NEXT_" + pf)

    # return it!
    return ftrs

if __name__ == "__main__":
    sents = [
    [ "I", "love", "food" ]
    ]
    preprocess_corpus(sents)
    for sent in sents:
        for i in xrange(len(sent)):
            print sent[i], ":", token2features(sent, i)
