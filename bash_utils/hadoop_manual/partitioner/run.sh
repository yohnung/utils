#!/bin/bash
# @Author: wanglinjie
# @Date:   2019-02-14 11:17:54
# @Last Modified by:   wanglinjie
# @Last Modified time: 2019-02-14 13:35:04
CMD="hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar"
CMD="${CMD} -D mapred.job.name=a_missingverb"
CMD="${CMD} -D mapred.map.tasks=2000"
CMD="${CMD} -D mapred.reduce.tasks=96"
CMD="${CMD} -D mapreduce.job.running.map.limit=2000"
CMD="${CMD} -D mapreduce.job.running.reduce.limit=96"
CMD="${CMD} -D mapred.reduce.slowstart.completed.maps=1"
CMD="${CMD} -D mapreduce.job.queuename=webrank"
CMD="${CMD} -D mapreduce.map.memory.mb=4096"
CMD="${CMD} -D mapreduce.task.timeout=1200000"
CMD="${CMD} -D mapreduce.reduce.memory.mb=8192"
CMD="${CMD} -D mapreduce.reduce.java.opts=-Xmx3000M"
#CMD="${CMD} -D mapreduce.map.memory.mb=3096"
#CMD="${CMD} -D mapreduce.map.java.opts=-Xmx3000M"
#CMD="${CMD} -D mapred.job.priority=VERY_HIGH"
#CMD="${CMD} -D yarn.app.mapreduce.am.resource.mb=2000"
#CMD="${CMD} -D yarn.app.mapreduce.am.command-opts=-Xmx1800m"
#CMD="${CMD} -D mapreduce.input.fileinputformat.split.minsize=2000000000"
#CMD="${CMD} -D mapreduce.input.fileinputformat.split.maxsize=2000000000"
#CMD="${CMD} -D mapred.output.compress=true"
#CMD="${CMD} -D mapred.output.compression.type=BLOCK"
#CMD="${CMD} -D mapred.output.compression.codec=com.hadoop.compression.lzo.LzopCodec"
#CMD="${CMD} -D map.output.key.field.separator=@#$"
#CMD="${CMD} -D mapred.text.key.partitioner.options=-k1,1"
#CMD="${CMD} -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner"
CMD="${CMD} -D num.key.fields.for.partition=1"
CMD="${CMD} -D stream.num.map.output.key.fields=2"
CMD="${CMD} -D mapred.text.key.comparator.options=\"-k1,2\" "
CMD="${CMD} -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner"
CMD="${CMD} -file map1.py"
CMD="${CMD} -file reduce.py"
CMD="${CMD} -mapper map1.py"
CMD="${CMD} -reducer reduce.py"

#for i in $( seq -w 1 12)
#do

# CMD="${CMD} -input /user/webrank/clicklog/ms_title/20181*/*/part*"
#CMD="${CMD} -input /user/webrank/sunfumin/queryurltitle_new/sogou/wap/2018*/*"
#CMD="${CMD} -input /user/webrank/sunfumin/queryurltitle_new/sogou/pc/*/*"
#CMD="${CMD} -output /user/webrank/lianghuashen/zjm_step_00/wap_again/2018"
# CMD="${CMD} -output /user/webrank/wanglinjie/click_title/20181"

# hadoop fs -rmr  /user/webrank/wanglinjie/click_title/20181
# CMDCMD="${CMD} -input /user/webrank/wanglinjie/anchor/data/term_freq1"
# CMDCMD="${CMDCMD} -output /user/webrank/wanglinjie/anchor/data/term_freq1_unigram_filter"

# hadoop fs -rmr /user/webrank/wanglinjie/anchor/data/term_freq1_unigram_filter

# CMDCMD="${CMD} -input /user/webrank/wanglinjie/anchor/data/bigram_ratio2"
# CMDCMD="${CMDCMD} -output /user/webrank/wanglinjie/anchor/data/term_freq1_bigram_filter"

# hadoop fs -rmr /user/webrank/wanglinjie/anchor/data/term_freq1_bigram_filter

#CMDCMD="${CMD} -input hdfs://master001.diablo.hadoop.nm.ted:8020/online/la/norm/norm_index_url_now/"
#CMDCMD="${CMDCMD} -input hdfs://master001.diablo.hadoop.nm.ted:8020/online/pagetitle/title.site_title_cut/"
CMDCMD="${CMD} -input hdfs://rsync.master003.polaris.hadoop.js.ted:8020/gpu-storage/liuqiuzhi/nasm/input/for_distill_infer_0805_random/"
CMDCMD="${CMDCMD} -output chenwenming/data_for_distill/"

hadoop fs -rmr chenwenming/data_for_distill/ 

# CMDCMD="${CMDCMD} -output /user/webrank/wanglinjie/anchor/data/term_freq_trigram"

# hadoop fs -rmr /user/webrank/wanglinjie/anchor/data/term_freq_trigram
echo Running command: ${CMDCMD}
${CMDCMD}
#done
