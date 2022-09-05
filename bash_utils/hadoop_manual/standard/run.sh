#!/bin/bash
# @Author: wanglinjie
# @Date:   2019-02-14 11:17:54
# @Last Modified by:   wanglinjie
# @Last Modified time: 2019-02-14 13:35:04
CMD="hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar"
CMD="${CMD} -D mapred.job.name=a_missingverb"
CMD="${CMD} -D mapred.map.tasks=2000"
CMD="${CMD} -D mapred.reduce.tasks=200"
CMD="${CMD} -D mapreduce.job.running.map.limit=2000"
CMD="${CMD} -D mapreduce.job.running.reduce.limit=2000"
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
CMD="${CMD} -file map.py"
CMD="${CMD} -file query.txt"
CMD="${CMD} -file reduce.py"
CMD="${CMD} -mapper map.py"
CMD="${CMD} -reducer reduce.py"

inputfile=/user/webrank/clicklog/ms/20200[4-7]/*/
CMDCMD="${CMD} -input ${inputfile}" 

outputfile="liuqiuzhi/dm/get_some_query/pv/step0_AMJJuly"
CMDCMD="${CMDCMD} -output ${outputfile}"

hadoop fs -rmr  ${outputfile}

echo Running command: ${CMDCMD}
${CMDCMD}
