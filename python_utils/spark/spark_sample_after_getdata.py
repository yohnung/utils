import random
import pyspark
import sys
import os
import numpy as np

def parse_dump_line(line,g_dd):
	index=line.find('#')
	first=line[:index].replace(',','')
	comment=line[index+1:]
	try:
		query,docid,pos,lq_rank,ltr_score = comment.strip().split('\t')
		s=float(ltr_score)
	except:
		pass
	frank=re.search(re.compile('1152:([-\.0-9]+)'),first).group(1)
	google_rank = -1
	key = query+'\t'+docid
	if key in g_dd:
		google_rank = g_dd[key]
	data=[query,docid,lq_rank,frank,ltr_score,google_rank]
	return 	data

def deal_ltr_dump_session(doclist,score_mean,score_std):
	#input doclist:list of [ 0:docid,1:lq_rank,2:frank,3:ltr_score,4:google_rank  ]
	#output: key=query,value=[0:docid,1:lq_rank,2:frank,3:ltr_score,4:google_rank,5:lq_pos,6:frank_pos,7:ltr_pos,8:ltr_zscore]
	rankByLq=sorted(doclist,key=lambda t:-float(t[1]))
	rankByFrank=sorted([t+[i] for (i,t) in enumerate(rankByLq)],key=lambda t:-float(t[2]))
	rankByLtr=sorted([t+[i] for (i,t) in enumerate(rankByFrank)],key=lambda t:-float(t[3]))
	rank_v = [t+[i] for (i,t) in enumerate(rankByLtr)]
	new_v = [ t+[ round( (float(t[3]) - score_mean )/score_std ,2) ] for t  in rank_v]
	return new_v

def load_data(ltr_dump_file,google_file,data_file):
	#output sorted_data: key:query value:[0:docid,1:lq_rank,2:frank,3:ltr_score,4:google_rank,5:lq_pos,6:frank_pos,7:ltr_pos,8:ltr_zscore]
	
	g_dd={}
	#0:query,1:docid,2:rank,3:wap_url
	google_data = sc.textFile(google_file,10).map(lambda x:x.strip().split('\t')).map(lambda l:('\t'.join(l[:2]),int(l[2])))	
	for k,v in google_data.collect():
		g_dd[k]=v
	#[0:query,1:docid,2:lq_rank,3:frank,4:ltr_score,5:google_rank]
	ltr_data = sc.textFile(ltr_dump_file,1000).filter(lambda x:x.strip()!='').map(lambda x:parse_dump_line(x.strip(),g_dd) )	
	ltr_data.persist()
	ltr_score_mean = ltr_data.map(lambda l:float(l[4])).mean()
	ltr_score_std = ltr_data.map(lambda l:float(l[4])).stdev()
	print 'score mean:%.3f score std:%.3f'%(ltr_score_mean,ltr_score_std)
	
	#deal with session
	temp = ltr_data.map(lambda l:(l[0],[l[1:]])).reduceByKey(lambda a,b:a+b)
	fix_std = round(ltr_score_std,2)
	#sorted_data: key:query value:[0:docid,1:lq_rank,2:frank,3:ltr_score,4:google_rank,5:lq_pos,6:frank_pos,7:ltr_pos,8:ltr_zscore]
	sorted_data = temp.map(lambda (k,v):(k,deal_ltr_dump_session(v,ltr_score_mean,fix_std  )))
	sorted_data.persist()
	print 'query_num:%d item_num:%d'%(sorted_data.count(),sorted_data.map(lambda (k,v):len(v)).sum() )
	ltr_data.unpersist()
	return sorted_data	

def sample_more_in_session_byscore(doc_list,norm_sample_scale = 3,ab_sample_scale = 3):
	#list of [0:docid,1:lq_rank,2:frank,3:ltr_score,4:google_rank,5:lq_pos,6:frank_pos,7:ltr_pos,8:ltr_zscore]
	#output_schema:part_index,label,docid,lq_rank,frank,ltr_score,google_rank,lq_pos,frank_pos,ltr_pos,ltr_zscore
	# (-2,3.5) -> (0,5)
	
	def scale(score):
		min_z=-2
		min_label = 0
		max_z=3.5
		max_label = 5
		if score<min_z:return min_label
		new_score = (score - min_z)* ((max_label - min_label)/(max_z-min_z) )
		return new_score
	def sample_and_label_score(sorted_list,num):
		#label,docid,lq_rank,frank,ltr_score,lq_pos,frank_pos,ltr_pos,ltr_zscore		
		if len(sorted_list)==0 :return []
		else:
			result=[]
			if num>len(sorted_list):
				num=len(sorted_list)
			for t in random.sample(sorted_list,num):
				result.append(t)
		return result
	
	
	
	#scale ltr_zscore
	temp_list = [[scale(t[8]) ] + t for t in doc_list]
	slist = sorted(temp_list,key=lambda t:-t[-1])
	part_index = 0
	result=[]
	
	for i in range(norm_sample_scale):
		sample_list=[slist[i]]
		top_label = slist[i][0]
		sample_list+= sample_and_label_score([t for t in slist[i+1:] if top_label-1.0>t[0] >=top_label-2.0 ] ,1)	
		sample_list+= sample_and_label_score([t for t in slist[i+1:] if top_label-2.0> t[0] >=top_label-3.0 ] ,1)	
		sample_list+= sample_and_label_score([t for t in slist[i+1:] if top_label-3.0> t[0] >=top_label-4.0 ] ,1)	
		sample_list+= sample_and_label_score([t for t in slist[i+1:] if top_label-4.0> t[0] >=top_label-5.0 ] ,1)	
		sample_list+= sample_and_label_score([t for t in slist[i+1:] if top_label-5.0> t[0] >=0 ] ,1)	
		result += [[str(part_index)]+ [str(x) for x in t] for t in sample_list]
		part_index +=1
	#pdb.set_trace()
	
	#0:label,1:docid,2:lq_rank,3:frank,4:ltr_score,5:google_rank,6:lq_pos,7:frank_pos,8:ltr_pos,9:ltr_zscore	
	def sample_around(sorted_list,begin,score,num,threshold):
		#random num sample around score
		#desc
		if len(sorted_list)==0 :return []
		end=len(sorted_list)-1
		while begin<end:
			mid = (begin+end)/2
			mid_label = sorted_list[mid][0]
			if mid_label == score:break
			if  score > mid_label :
				end = mid -1 
			else:
				begin = mid+1
		mid = (begin+end)/2
		temp = [ t for t in  sorted_list[max(mid-1,0):mid+1]  if abs(score-t[0])<threshold ]
		#pdb.set_trace()
		
		if num>len(temp):
			num=len(temp)
		
		return (mid,random.sample(temp,num))

	all_google_list = [(i,t) for i,t in enumerate( slist) if t[5] > -1 and t[5]<=5]
	ab_list=[]
	index = 0
	if len(all_google_list)>0:
		#pdb.set_trace()
		for i,good in all_google_list:
			begin_index = 0
			google_list=[]
			google_rank = good[5]
			google_label = slist[google_rank][0]
			if i>100 and google_label - good[0]>1.0: #is_ab
				begin_index = 10000
			'''	
			nmid,google_sample_list = sample_around(slist,0,google_label-0.5,1,0.5)	
			
			nmid,tlist = sample_around(slist,nmid,google_label-1,1,0.5)
			google_sample_list+=tlist
			
			nmid,tlist = sample_around(slist,nmid,google_label-2,1,0.5)
			google_sample_list+=tlist
			
			nmid,tlist = sample_around(slist,nmid,google_label-3,1,0.5)
			google_sample_list+=tlist

			nmid,tlist = sample_around(slist,nmid,google_label-4,1,0.5)
			google_sample_list+=tlist
			
			nmid,tlist = sample_around(slist,nmid,google_label-5,1,0.5)
			google_sample_list+=tlist
			'''
			google_sample_list = sample_and_label_score([t for t in slist[google_rank:] if abs(google_label - 0.5 - t[0])<0.1 and t[5]<0 ] ,1)		
			google_sample_list += sample_and_label_score([t for t in slist[google_rank:] if abs(google_label - 1 - t[0])<0.2 and t[5]<0 ] ,1)		
			google_sample_list += sample_and_label_score([t for t in slist[google_rank:] if abs(google_label - 2 - t[0])<0.2 and t[5]<0 ] ,1)		
			google_sample_list += sample_and_label_score([t for t in slist[google_rank:] if abs(google_label - 3 - t[0])<0.2 and t[5]<0 ] ,1)		
			google_sample_list += sample_and_label_score([t for t in slist[google_rank:] if abs(google_label - 4 - t[0])<0.2 and t[5]<0 ] ,1)		
			google_sample_list += sample_and_label_score([t for t in slist[google_rank:] if abs(google_label - 5 - t[0])<0.2 and t[5]<0 ] ,1)		
			
			if len(google_sample_list) == 0:continue
			google_sample_list.append([google_label]+good[1:])
			ab_list += [[str(begin_index+index)]+[str(x) for x in t] for t in google_sample_list ]
			index+=1
			#pdb.set_trace()		
	
	return (result,ab_list)
	

def get_sample_label_data(sorted_data,output_sample_file,mark_key_file):

	temp = sorted_data.map(lambda (k,v):(k,sample_more_in_session_byscore(v) ))
	
	


if __name__=='__main__':
	
	conf = SparkConf()
	sc = SparkContext(conf=conf)
	sqlContext=HiveContext(sc)
	sc.setLogLevel('WARN')

	ltr_dump_file = '/user/webrank/huxinchen/ltr/data/job_1558772456293_2608/ltrs/ltr.test.query/'
	google_file = '/user/webrank/huxinchen/ltr/google_docid_result/google_result_docid_201905'
	if len(sys.argv)>2:
		google_file = sys.argv[2]
	data_file=ltr_dump_file+'.sort_data'
	more_ab_file=ltr_dump_file+'.more_ab_file'
	key_file=ltr_dump_file+'.mark_query_docid'

	data=load_data(ltr_dump_file,google_file,data_file)
	get_sample_label_data(data,more_ab_file,key_file)
