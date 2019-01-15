#!/usr/bin/env python
from __future__ import division 
import sys, fileinput
import tree
import collections
import json

count_word = {}
count_rules = {}
sum_rules = 0
sum_words = 0
max_rule = 0
max_word = 0
sum_rules_num = 0

for line in fileinput.input():
	t = tree.Tree.from_str(line)
	for node in t.bottomup():
		if len(node.children) == 2:
			s = node.children[0].label + " " + node.children[1].label
			if count_rules.has_key(node.label):
				count_rules[node.label][s] += 1
			else:
				count_rules[node.label] = collections.defaultdict(int)
				count_rules[node.label][s] += 1
		if len(node.children) == 1:
			if count_word.has_key(node.label):			#has the key
				count_word[node.label][node.children[0].label.lower()] += 1
			else:
				count_word[node.label] = collections.defaultdict(int)
				count_word[node.label][node.children[0].label.lower()] += 1

# for key in count_rules:
# 	sum_rules += len(count_rules[key])
# for key in count_word:
# 	sum_words += len(count_word[key])
# print sum_rules+sum_words

for key in count_rules:
	dictionary = count_rules[key]
	sum_rules_num = 0
	for sub_key in dictionary:
		# if dictionary[sub_key] > max_rule:
		# 	max_rule = dictionary[sub_key]
		# 	rule = key + "->" + sub_key
		sum_rules_num += dictionary[sub_key]
	for sub_key in dictionary:
		dictionary[sub_key] = float(dictionary[sub_key]/sum_rules_num)
		

for key in count_word:
	dictionary = count_word[key]
	sum_word_num = 0
	for sub_key in dictionary:
		# if dictionary[sub_key] > max_word:
		# 	max_word = dictionary[sub_key]
		# 	word = key + "->" + sub_key
		sum_word_num += dictionary[sub_key]
	for sub_key in dictionary:
		# print dictionary[x]
		# print sum_word_num
		dictionary[sub_key] = float(dictionary[sub_key]/sum_word_num)


# print max_word, word
# print max_rule, 
s = json.dumps(count_rules)
s2 = json.dumps(count_word)
print s,'\n',s2
	





    
    
