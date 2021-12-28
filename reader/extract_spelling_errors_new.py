# -*- coding: utf-8 -*-
import codecs
import utils
import re
import sys
from nltk.metrics import edit_distance
import opencc
import string
import math
converter = opencc.OpenCC('t2s.json')


def hasNumbers(inputString):
	return bool(re.search(r'\d',inputString))

def hasBrackets(inputString):
	return bool(re.search(r'\[|\]|\)|\(',inputString))

def hasAlphabets(inputString):
	return bool(re.search(r'[a-zA-Z]',inputString))

def hasSpecialCharacters(inputString):
	return bool(re.search(r'[\|\s]',inputString))

def create_files(fname):
	# files = codecs.open(output+ '/' + fname +  "_spelling_error.txt","w", encoding='utf-8')
	cf = codecs.open(output+ '/' + fname +  "_orig_sen.txt","w", encoding='utf-8')
	ef = codecs.open(output+ '/' + fname +  "_error_sen.txt","w", encoding='utf-8')
	return ef,cf

def check_error(earlier,current, srcs,tgts,number_of_edits):
	earlier = utils.split_sentence(earlier)
	current = utils.split_sentence(current)
	if len(earlier)==len(current):
		for j in range(0, len(earlier)):
			f=0
			earlier_words = earlier[j]
			current_words = current[j]
			if earlier_words == current_words:
				continue
			if len(earlier_words) < 5:
				continue
			if sum([1 if utils.is_chinese_char(x) else 0 for x in current_words]) / len(current_words) <= 0.7:
				continue

			if(len(earlier_words) == len(current_words)):
				for k in range(0,len(earlier_words)):
					if earlier_words[k]==current_words[k]:
						continue
					elif utils.is_chinese_char(earlier_words[k]):
						f += 1

			thr = min(max(math.ceil(number_of_edits * len(current_words)),1),10)
			if(1<=f<=thr):
				srcs.append(earlier[j])
				tgts.append(current[j])

if __name__ == '__main__':

	source = sys.argv[1]+"/"
	source += sys.argv[2]
	language = sys.argv[4]
	number_of_edits = float(sys.argv[5])
	output = sys.argv[3]
	
	files,files_2,files_3 = None,None,None
	revisions = []
	line = []
	f=0

	srcs,tgts = [],[]
	pre_revision = ''
	current_revision = ''
	cnt = 0
	for line in open(source):
		line = converter.convert(line)
		if "Revision timestamp" in line:
			if current_revision:
				if pre_revision:
					cnt += 1
					if cnt % 100 == 0:
						print(source,'processed',cnt)
					check_error(pre_revision,current_revision.strip(),srcs,tgts,number_of_edits)
			pre_revision = current_revision.strip()
			current_revision = ''
		else:
			current_revision += line
	if current_revision and pre_revision:
		check_error(pre_revision,current_revision.strip(),srcs,tgts,number_of_edits)

	
	if srcs:
		ef,cf = create_files(sys.argv[2])
		errors = set()
		for src,tgt in zip(srcs[::-1],tgts[::-1]):
			if src in errors or tgt in errors:
				continue
			errors.add(src)
			errors.add(tgt)
			ef.write(src + '\n')
			cf.write(tgt + '\n')

		ef.close()
		cf.close()
