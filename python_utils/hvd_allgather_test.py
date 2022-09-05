# coding=utf8
import tensorflow as tf
import horovod.tensorflow as hvd

hvd.init()

config = tf.ConfigProto()
config.gpu_options.visible_device_list = str(hvd.local_rank())

# the same for every process
v = tf.get_variable("v", shape=(1,2), initializer=tf.random_normal_initializer(0.0, 1e-2))	# v = (x,y)

# different for different process
data = tf.constant([[1.* hvd.rank() + 1, 2. * hvd.rank() + 1], [3. * hvd.rank() + 1, 4.* hvd.rank() + 1]]) # shape=[2,2]
# rank-0: [[1,1], [1,1]], rank-1: [[2,3], [4,5]], rank-2: [3,5],[7,9], rank-3: [4,7],[10,13]

mid = tf.reshape(tf.matmul(data, v, transpose_b=True) - 1, [1, -1]) # [1, 2]

# all-gather
print "dimension", mid
mid_all = hvd.allgather(mid)  # [n_gpu, 2]
print "dimension", mid_all

loss = tf.reduce_sum(tf.square(mid_all))

grad = tf.gradients(loss, [v])

opt = tf.train.GradientDescentOptimizer(0.1)
opt = hvd.DistributedOptimizer(opt)

hooks = None
hooks = [hvd.BroadcastGlobalVariablesHook(0)]

train_op = opt.minimize(loss)

with tf.train.MonitoredTrainingSession(config=config, hooks=hooks) as sess:
	for i in range(2):
		var_ = sess.run(v)
		_, loss_, grad_ = sess.run([train_op, loss, grad])
		print("rank-"+str(hvd.rank())+", v="+str(var_)+", loss="+str(loss_)+", grad="+str(grad_[:][0]))

