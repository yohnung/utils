with open('./94.3_videoalbert.inference.mini_recall', 'r') as first_file, open('lr5e-7_randomneg_ckpt200_videoalbert.inference.mini_recall', 'r') as second_file,\
     open('both_right', 'w') as right_file, open('94_3_right', 'w') as first_right_file,\
     open('94_1_right', 'w') as second_right_file, open('both_wrong', 'w') as wrong_file, \
     open('err.txt', 'w') as err_file:
    for first_line in first_file:
        first_seg = first_line.strip().split('\t')
        first_scores = [float(first_seg[15]), float(first_seg[16])]

        second_line = next(second_file)
        second_seg = second_line.strip().split('\t')
        try:
            second_scores = [float(second_seg[15]), float(second_seg[16])]    #int(second_seg[3])  #
        except:
            err_file.write(second_line)
            continue

        first_cond = (first_scores[0] > first_scores[1])
        second_cond = (second_scores[0] > second_scores[1])    #second_scores 

        if first_cond and second_cond:
            right_file.write('\t'.join(second_seg[:15]) + '\n')
        elif (not first_cond) and (not second_cond):
            wrong_file.write('\t'.join(second_seg[:15]) + '\n')
        elif first_cond:
            first_right_file.write('\t'.join(first_seg[:]) + '\n')
        else:
            second_right_file.write('\t'.join(second_seg[:]) + '\n')

