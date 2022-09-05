import numpy as np

def postprocess(scoreList, itemList):
    scoreList.sort(key=lambda arg: arg[0])                  # scoreList = [(score1, [item1_index, item2_index, ...]), (...), (...)]
    maskList = [False for i in range(len(itemList))]        # itemList = [item1, item2, item3, ...]
    
    res_file = open('cacheltr.eval.input', 'a') 

    prob = 1.0
    np.random.seed(len(scoreList))

    flag_stop = True if len(scoreList) < 2 else False       # at least, there should be 2 different scores

    while not flag_stop:
        index1, index2 = np.random.choice(len(scoreList), 2, False) # pick up 2 random scores
        pickedlist = [scoreList[index1], scoreList[index2]]
        pickedlist.sort(key=lambda arg: arg[0])

        good_item_index = np.random.choice(pickedlist[1])
        bad_item_index = np.random.choice(pickedlist[0])
        if not (maskList[good_item_index] and maskList[bad_item_index]):
            maskList[good_item_index] = True
            maskList[bad_item_index] = True
            
            if np.random.random() < prob and (pickedlist[1][0] - pickedlist[0][0] > 1.9):
                good_item = itemList[good_item_index]
                bad_item = itemList[bad_item_index].split('\t')

                res_file.write(good_item + '\t' + '\t'.join(bad_item[1:]) + '\n')
        else:
            if False in maskList:
                flag_stop = False
            else:
                flag_stop = True
    pass 
        

old_qid = 0
scoreList = []
itemList = []
# ltr.train.query is more rich of data
with open('./ltr.train.query.allign_with_nasm', 'r') as score_file, open('./ltr.nasm', 'r') as train_file:
    for line in score_file:
        line = line.strip().split(' #')
        features = line[0].split(' ')
        qnum = features[1].split(':')[1]
        qnum = ''.join(qnum.split(','))
        qid = int(qnum)
        score = float(features[0])
        if (not qid == old_qid) and score > -0.2:           
            postprocess(scoreList, itemList)            # process the constructed scoreList and itemList

            item_num = 0
            scoreList = []                   # component = (float(score), list(item_num_list))
            itemList = []

            scoreList.append((score, [item_num]))
            
            itemList.append(next(train_file).strip())

            old_qid = qid
        elif score > -0.2:                                # qid == old_qid, under the same query, construct itemList with scores
            item_num += 1
            flag_append = False
            for index, comp in enumerate(scoreList):      # scoreList = [(score, [item1_num, ...]), (score2, [item1_num, item2_num])]
                if score == comp[0]:
                    scoreList[index][1].append(item_num)
                    flag_append = True
                    break
            if not flag_append:
                scoreList.append((score, [item_num]))

            itemList.append(next(train_file).strip())     # corresponding to scoreList
        else:
            next(train_file)
