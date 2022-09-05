#!/usr/bin/python
#encoding=gbk

import sys
import xml.etree.ElementTree as ET
from urllib import unquote
import re

punc_char=set([' ', '　',  ',', '，', '。', '?', '？', '!', '！'])
def tokenize(string):
	'''
	string: a unicode-sequence
	
	'''
	res = []
	is_start = True
	for word in string:
		if word in punc_char:
			continue
			is_start = True
		if ord(word) > 0x4E00 and ord(word) < 0x9FFF:	# chinese character
			res.append(word)
			is_start = True
		elif is_start:
			res.append(word)
			is_start = False
		else:
			res[-1]+=word
	return res

def compare(text_1, text_2, flag):
	''' all variables are unicode 
            title and content contains '<em> *** </em>' enclosing relevant terms '''
	## to compute relevance of two pieces of text, the simplest way is to compute bm25 score which considers term-match and term-frequency
	## although bm25-score is coarse
	
	## owing to baidu-searched results highlight relevant terms, we just compute the ratio relevant-terms' length to query_length to indicating the relevance
	## furtherly, we could take synonum terms in query to compute the ratio
	if not text_2:
		return False
	text_1_tok = tokenize(text_1)
	length_1 = len(text_1_tok)
	assert length_1 > 0
	is_matched = [0 for x in range(length_1)]
	term2index = {}
	for i in range(length_1):
		if text_1_tok[i] in term2index:
			term2index[text_1_tok[i]].append(i)
		else:
			term2index[text_1_tok[i]] = [i]
	
	relterm_pattern = re.compile('<em>(.*?)</em>')
	relevant_terms = set()
	for match in relterm_pattern.finditer(text_2):
		term = match.group(1)
		relevant_terms.add(term)
	
	# simplest way to find how many terms are common
	for term in relevant_terms:
		for sub_term in tokenize(term):
			if sub_term in term2index and len(term2index[sub_term]) > 0:
				index = term2index[sub_term][0]
				is_matched[index] = 1
				term2index[sub_term].pop(0)
	matched_count = 0
	for i in range(length_1):
		matched_count += is_matched[i]
	
	match_ratio = 1.0 * matched_count / length_1
	
	if flag == 'fine':
		if match_ratio > 0.85:
			return True
		return False
	elif flag == 'medium':
		if match_ratio > 0.30:
			return True
		return False
	elif flag == 'coarse':
		if match_ratio > 0.10:
			return True
		return False
	

#tmpf = open('./demo.txt')
#for line in tmpf:
for line in sys.stdin:
	line = line.strip()
	data = line.split('\t')
	if (len(data) > 1):
		query = unquote(data[0].split('&')[0].split('query=')[1]).decode('utf8')	# is utf-8
		if not query:
			continue
                query_tok = tokenize(query)	# a character sequence 
		if len(query_tok) < 4:
			continue
		
		xml = '\t'.join(data[1:])
		try:
			root = ET.fromstring(xml)
		except:
			continue
		
		first = True
		for item in root.findall('.//display'):
			if first:
				first = False	
				continue
			
			url = item.find('url').text	# could contain chinese-character string(unicoded)
			if not (url and url.startswith("http")):	# is unicode
				continue
			if url.startswith('https://m.baidu.com') or \
			   url.startswith('http://m.baidu.com') or \
			   url.startswith('https://tieba.baidu.com') or \
			   url.startswith('http://tieba.baidu.com') or \
			   url.startswith('https://wk.baidu.com') or \
			   url.startswith('http://wk.baidu.com') or \
			   url.startswith('https://baijiahao.baidu.com') or \
			   url.startswith('http://baijiahao.baidu.com'):
				continue
			
			title = item.find('title').text
			if not title:
				continue
			
			content = item.find('content').text
			if not content:
				continue
			
			#print(query+'\t'+title+'\t'+content+'\t'+url)
			if (not compare(query, title, 'coarse')) and compare(query, content, 'fine'):
				print(query.encode('gb18030')+'\t'+title.encode('gb18030')+'\t'+content.encode('gb18030')+'\t'+url.encode('gb18030'))	
			#else:
			#	sys.stderr.write(query+'\t'+title+'\t'+content+'\t'+url+'\n')
