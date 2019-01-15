#!/usr/bin/env python
import sys,time
import json
import argparse
import codecs
if sys.version_info[0] == 2:
  from itertools import izip
else:
  izip = zip
import gzip
import numpy as np
import math
import copy
import matplotlib


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

def print_tree(key, node, back):
	if type(node) is list:
		if len(node) == 1:
			return "({} {})".format(key, node[0])
		else:
			left_key = node[0][2]
			left_child = back[node[0][0]][node[0][1]][left_key]
			l = print_tree(left_key, left_child, back)
			right_key = node[1][2]
			right_child = back[node[1][0]][node[1][1]][right_key]
			r = print_tree(right_key, right_child, back)
		return "({} {} {})".format(key,l,r)
	else:
		return "()"

def main():
	parser = argparse.ArgumentParser(description="ignore input; make a demo grammar that is compliant in form",
	                               formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("--infile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input file (ignored)")
	parser.add_argument("--rulesfile", "-r", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input file (ignored)")
	parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file (grammar)")

	try:
		args = parser.parse_args()
	except IOError as msg:
		parser.error(str(msg))

	infile = prepfile(args.infile, 'r')
	rulesfile = prepfile(args.rulesfile, 'r')
	outfile = prepfile(args.outfile, 'w')

  	#get my grammars
  	count_line = 0
	for line in rulesfile:
		if count_line == 0:
			dictionary_rule = json.loads(line)
		else:
			dictionary_word = json.loads(line)
		count_line += 1

	# Viter CKY
	# first_line = infile.readline().strip()
	# w = first_line.split(" ")		
	# length = len(w)
	word_list = dictionary_word.keys()
	rules_list = dictionary_rule.keys()
	whole_list = []
	whole_list = word_list + rules_list
	d = {}
	for x in whole_list:
		d[x] = float("-inf")

	for line in iter(infile):
		w = line.strip().split(" ")
		length = len(w)
		best = np.zeros((length+1, length+1)).tolist() 
		back = np.zeros((length+1, length+1)).tolist() 
		#replace unknown words with <unk>
		for i in range(length):
			unknown = True
			for key in dictionary_word:
				tmp_dict = dictionary_word[key]
				if tmp_dict.has_key(w[i].lower()):
					unknown = False
					break
			if unknown == True:
				w[i] = "<unk>"
		#initialize
		for i in range(len(w)):
			for j in range(i+1, len(w)+1):
				best[i][j] = copy.deepcopy(d)
				back[i][j] = copy.deepcopy(d)

		for i in range(1,len(w)+1):
			for key in dictionary_word:
				tmp_dict = dictionary_word[key]
				if tmp_dict.has_key(w[i-1].lower()):
					p = tmp_dict[w[i-1].lower()]
					if math.log10(p) > best[i-1][i][key]:
						best[i-1][i][key] = math.log10(p)
						back[i-1][i][key] = [w[i-1]]

		for l in range(2, len(w)+1):
			for i in range(len(w)+1-l):
				j = i + l
				for k in range(i+1, j):
					for key in dictionary_rule:
						tmp_dict = dictionary_rule[key]
						for subkey in tmp_dict:
							Y = subkey.split()[0]
							Z = subkey.split()[1]
							if best[i][k][Y] == float("-inf") or best[k][j][Z] == float("-inf"):
								continue
							else:
								log_p = math.log10(tmp_dict[subkey]) + best[i][k][Y] + best[k][j][Z]
								if log_p > best[i][j][key]:
									best[i][j][key] = log_p
									back[i][j][key] = [[i,k,Y],[k,j,Z]]

		outfile.write(print_tree("TOP", back[0][length]["TOP"], back) + "\n")

	#close all open files
	infile.close()
	outfile.close()
	rulesfile.close()


if __name__ == '__main__':
	main()

	


