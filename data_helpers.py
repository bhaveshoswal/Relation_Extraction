import pandas as pd
from nltk.tokenize import TweetTokenizer
import re
import os
import tensorflow as tf
import numpy as np
import gc

file_path = "/home/sahil/ML-bucket/train.csv"


def read_data(file=file_path):
    col_names = ['System-Id', 'Message', 'drug-offset-start', 'drug-offset-end', 'sideEffect-offset-start',
                 'sideEffect-offset-end', 'WM1', 'WM2', 'relType']
    data_frame = pd.read_csv(file, skipinitialspace=True, usecols=col_names)
    mssg_frame = data_frame['Message'].drop_duplicates()
    tokenizer = TweetTokenizer()
    string = []
    for mssg in mssg_frame:
        tokens = tokenizer.tokenize(mssg)
        for token in tokens:
            if is_word(token):
                string.append(token.lower())
    if not os.path.isfile("words.txt"):
        with open("words.txt", "w") as text_file:
            print(string, file=text_file)
    return data_frame


# TODO use space splitter and then strip the word
# TODO change regex to [a-z0-9].+
def is_word(word):
    if re.match(r'\A[\w]+\Z', word):
        return True
    return False


def word2id(word):
    word = 'b\'' + word + '\''
    with open("data/vocab.txt") as f:
        for i, line in enumerate(f):
            if line.split()[0] == word:
                return i
    return -1


#
# class w2v(object):
#     def __init__(self):
#         tf.load_op_library(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'word2vec_ops.so'))
#         metafile = str(tf.train.get_checkpoint_state("data").model_checkpoint_path) + ".meta"
#         self.sess = tf.Session()
#         new_saver = tf.train.import_meta_graph(metafile)
#         new_saver.restore(self.sess, tf.train.latest_checkpoint("data"))
#         self.all_vars = tf.trainable_variables()
#         init_op = tf.global_variables_initializer()
#         self.sess.run(init_op)
#
#     def get_word_vector(self, word):
#         if word != "UNK":
#             word = word.lower()
#         index = word2id(word)
#         if index == -1:
#             raise ValueError("{} doesn't exist in the vocablury.".format(word))
#         else:
#             yield (self.sess.run(self.all_vars[3][index]))
#
#     def close_session(self):
#         del self.sess

def get_word_vector():
    tf.load_op_library(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'word2vec_ops.so'))
    metafile = str(tf.train.get_checkpoint_state("data").model_checkpoint_path) + ".meta"
    sess = tf.Session()
    new_saver = tf.train.import_meta_graph(metafile)
    new_saver.restore(sess, tf.train.latest_checkpoint("data"))
    all_vars = tf.trainable_variables()
    init_op = tf.global_variables_initializer()
    sess.run(init_op)
    yield sess.run(all_vars[3])


def batch_iter(doc, batch_size, num_epochs, shuffle=True):
    """
    Generates a batch iterator for a dataset.
    """
    data = list()
    for iter in doc:
        data.append(iter)
    # print("len", len(data))
    data = np.array(data)
    print(data)
    data_size = len(data)
    num_batches_per_epoch = int((len(data) - 1) / batch_size) + 1
    for epoch in range(num_epochs):
        # Shuffle the data at each epoch
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            shuffled_data = data[shuffle_indices]
        else:
            shuffled_data = data
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)
            yield shuffled_data[start_index:end_index]
