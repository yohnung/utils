import pickle as pkl
import collections
import pandas as pd
import os

inference_data_file = '/search/odin/results/bert/lqzhr2data_finetune_margin0.1/inference.ckpt_3.txt'
processed_inference_data_file = '/search/odin/results/bert/lqzhr2data_finetune_margin0.1/inference.ckpt_3.pd'
eval_data_file = '/search/odin/data/recall_infer_data/mini_recall.eval.input'

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
    queries = []
    doc1titles, doc1values, doc1_keyword1, doc1_keyword2 = [], [], [], []
    doc2titles, doc2values, doc2_keyword1, doc2_keyword2 = [], [], [], []
    try:
        with open(inference_data_file, 'rb') as infer_file, open(eval_data_file, 'rb') as eval_file:
            for line in infer_file:
                line = line.strip().split(b'\t')                                   # decode the string to unicode charactors
                if len(line) > 1:
                    full_line = next(eval_file).strip().split(b'\t')
                    queries.append(line[0].decode('gbk'))
                    doc1titles.append(line[1])
                    doc1values.append(line[2])
                    doc1_keyword1.append(full_line[3])
                    doc1_keyword2.append(full_line[4])
                    doc2titles.append(line[3])
                    doc2values.append(line[4])
                    doc2_keyword1.append(full_line[10])
                    doc2_keyword2.append(full_line[11])
    except:
        print("please check the recall_evaluation data\n")

    cryp2word_dict = read_vocab("/search/odin/word_list/vocab_tiny_full_573780")    # it's 'gbk' encoded
    cryp2word_dict = collections.defaultdict(lambda: u'<unk>'.encode('gbk'), cryp2word_dict)

    for i in range(len(doc1titles)):
        doctitle = doc1titles[i].split()
        title = ''.encode('gbk')
        for wordid in doctitle:
            title += cryp2word_dict[wordid]
        doc1titles[i] = title.decode('gbk')

        keywords = doc1_keyword1[i].split()
        keyword = ''.encode('gbk')
        for keywordid in keywords:
            keyword += cryp2word_dict[keywordid] + ' '.encode('gbk')
        doc1_keyword1[i] = keyword.strip().decode('gbk')

        keywords = doc1_keyword2[i].split()
        keyword = ''.encode('gbk')
        for keywordid in keywords:
            keyword += cryp2word_dict[keywordid] + ' '.encode('gbk')
        doc1_keyword2[i] = keyword.strip().decode('gbk')

        doctitle = doc2titles[i].split()
        title = ''.encode('gbk')
        for wordid in doctitle:
            title += cryp2word_dict[wordid]
        doc2titles[i] = title.decode('gbk')

        keywords = doc2_keyword1[i].split()
        keyword = ''.encode('gbk')
        for keywordid in keywords:
            keyword += cryp2word_dict[keywordid] + ' '.encode('gbk')
        doc2_keyword1[i] = keyword.strip().decode('gbk')

        keywords = doc2_keyword2[i].split()
        keyword = ''.encode('gbk')
        for keywordid in keywords:
            keyword += cryp2word_dict[keywordid] + ' '.encode('gbk')
        doc2_keyword2[i] = keyword.strip().decode('gbk')

    # here should make sure what encoding is used
    tmpzip = zip(doc1values, doc2values, doc1titles, doc1_keyword1, doc1_keyword2, doc2titles, doc2_keyword1, doc2_keyword2)
    pddata = pd.DataFrame(tmpzip, columns = [u'score-1', u'score-2', u'title-1', u'key-1-1', u'key-1-2', u'title-2', u'key-2-1', u'key-2-2'], index = queries)
    with open(processed_inference_data_file, 'wb') as file:
        pkl.dump(pddata, file)
    del title, tmpzip

    return 1

if __name__ == '__main__':
    if main():
        print('the translation is done')
