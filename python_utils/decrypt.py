import pickle as pkl
import collections
import pandas as pd
import os
import sys

eval_data_file = sys.argv[1]
result_file = sys.argv[2]

def read_vocab(vocabfile):
    ''' construct a dictinary `cryp2word_dict={id: word}` according to the given vocabulary
    '''

    cryp2word_dict = {}                                                       # result collections.defaultdict(lambda: "~unknown".encode('gbk'))

    filename = vocabfile+'.cryp2word.pkl'
    if os.path.exists(filename):
        file = open(filename, 'rb')
        cryp2word_dict = pkl.load(file)
        return cryp2word_dict

    try:
        with open(vocabfile+'.pkl', 'rb') as file:
            word_dict_orig = pkl.load(file)
            word_dict = collections.defaultdict(list)
            if word_dict_orig is None:
                print("This vocabulary has no items, please provide the right vocabulary.\n")
            else:
                for key in word_dict_orig:
                    word_dict[word_dict_orig[key]].append(key)                 # interchange key with value
    except:
        print("please check the given vocabulary\n")
        return cryp2word_dict

    del word_dict_orig
#   now, you have word_dict={word_id: [word, cryptic_word]}, with query or word is 'gbk' decoded

    for value in word_dict.values():
        if len(value) != 2:
            print('this word has no crypted one: ' + str(value))
        else:
            term1 = value[0]
            term2 = value[1]
            is_id = True
            for singstr in term1:
                is_id = is_id and ((singstr >= '0' and singstr <='9') or (singstr >= 'a' and singstr <= 'z'))
                if not is_id:
                    break
            if is_id:
                cryp2word_dict[term1] = term2
            else:
                cryp2word_dict[term2] = term1
    del word_dict

    with open(filename, 'wb') as file:
        pkl.dump(cryp2word_dict, file)

    return cryp2word_dict

def main():

    cryp2word_dict = read_vocab("/search/odin/word_list/vocab_tiny_full_573780")    # it's 'gbk' encoded
    cryp2word_dict = collections.defaultdict(lambda: u'<unk>'.encode('gb18030'), cryp2word_dict)

    try:
        with open(result_file, 'w') as write_file, open(eval_data_file, 'r') as eval_file:
            for line in eval_file:
                line_seg = line.strip().split('\t')
                
                doctitle = line_seg[1].split()
                title = ''.encode('gb18030')
                for wordid in doctitle:
                    title += cryp2word_dict[wordid] + ' '.encode('gb18030')
                line_seg[1] = title.strip()

                doctitle = line_seg[8].split()
                title = ''.encode('gb18030')
                for wordid in doctitle:
                    title += cryp2word_dict[wordid] + ' '.encode('gb18030')
                line_seg[8] = title.strip()

                write_file.write('\t'.join(line_seg) + '\n')
        return 1
    except:
        print("please check the recall_evaluation data\n")
        return 0


if __name__ == '__main__':
    if main():
        print('the translation is done')
