#!/bin/python
import codecs

location = []
f = codecs.open("data/lexicon/location", "r", encoding='utf-8')
location.extend(f.read().splitlines())
f.close
location = [item.lower() for item in location]
temp = []
f = open("data/lexicon/location.country", "r")
temp.extend(f.read().splitlines())
f.close
temp = [item.lower() for item in temp]
location.append(temp)

print location