#!/usr/bin/python
# coding = gbk
punc_char=set([' ', '¡¡',  ',', '£¬', '¡£', '?', '£¿', '!', '£¡'])
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
