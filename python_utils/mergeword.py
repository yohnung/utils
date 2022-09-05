#coding=utf-8
#python2
import sys

def _transform(word):
    '''
        if it is a full-width english character, turn it into a half-width english character, else do nothing
        if token is full-width white-space, change it to half-width white-space
        args:
            word: is a english-word or chinese word|character
    '''
    word_ans = ''
    token = word
    uni_token = ''
    if token == '<unk>':
        return uni_token
    for char in token:
        code_point = ord(char)
        if code_point == 12288:         # full-width white-space
            code_point = 32             # half-width white-space
        elif (code_point >= 65281 and code_point <= 65374):
            code_point -= 65248

        uni_token += unichr(code_point)
    return uni_token.strip()             # white space in the end of the wordence is removed, include the transformed half-width white-space

def _is_chinese_word(word):                 # maybe '我们'
    if not word:
        return False
    flag = True
    for char in word:
        cp = ord(char)
        if ((cp >= 0x4E00 and cp <= 0x9FFF) or
            (cp >= 0x3400 and cp <= 0x4DBF) or
            (cp >= 0x20000 and cp <= 0x2A6DF) or
            (cp >= 0x2A700 and cp <= 0x2B73F) or
            (cp >= 0x2B740 and cp <= 0x2B81F) or
            (cp >= 0x2B820 and cp <= 0x2CEAF) or
            (cp >= 0xF900 and cp <= 0xFAFF) or
            (cp >= 0x2F800 and cp <= 0x2FA1F)):
            flag = flag and True
        else:
            flag = flag and False
    return flag
 
def merge_chinese_character(sent):          # a sentence is a string like '中文词 english_and_number_string whole_width-white_space'
    tokens_list = map(lambda x: _transform(x.decode('gb18030')).encode('gb18030'), sent.split(' '))   # sentence is a gb18030 encoded
    # token_list is half-width character for a-z and 1-9
    for i in range(len(tokens_list)):
        if tokens_list[i] and (not _is_chinese_word(tokens_list[i].decode('gb18030'))):      # is it is a alphabatic and numeric
            tokens_list[i] = ' ' + tokens_list[i] + ' '           # wrap the word with ' '
    return ''.join(tokens_list).replace('  ', ' ').strip()        # maybe empty


for line in sys.stdin: #open('qltr.infer.input.decrypted.query_title'): #open('./fea_data.train.text.decrypted.query_title'): # it is gb18030 encoded sentence, maybe <unk>
    print merge_chinese_character(line.strip())
    
