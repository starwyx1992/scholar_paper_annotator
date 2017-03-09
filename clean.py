import os
import numpy as np
import nltk
import re
import pandas as pd
import distance 

filename='abstract.txt'

f=open(filename,'r')
rawtxt=f.readlines()

def tokenize_only(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    return tokens

tokens=tokenize_only(str(rawtxt))
indexlist=[]
## Find the index of <> in a tuple
for i in range(len(tokens)):
	if tokens[i]=='<': ##The start of junk message 
		sindex=i
	if tokens[i]=='>':
		eindex=i
		indexlist.extend(range(sindex,eindex+1))
		del sindex,eindex
cleantxt=[]
for i in range(len(tokens)):
	if i not in indexlist:
		cleantxt.append(tokens[i])

print cleantxt


	
# for i in indexlist:
# 	del 