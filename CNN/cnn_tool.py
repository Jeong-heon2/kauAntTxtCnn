#-*- coding:utf-8 -*-
import numpy as np
import pandas as pd
import re
import tensorflow as tf
import random
import hangle
import openpyxl


####################################################
# cut words function                               #
####################################################
def cut(contents, cut=2):
    results = []
    for content in contents:
        words = content.split()
        result = []
        for word in words:
            result.append(word[:cut])
        results.append(' '.join([token for token in result]))
    return results

####################################################
# divide train/test set function                   #
####################################################
def divide(x, y, train_prop):
    random.seed(1234)
    x = np.array(x)
    y = np.array(y)
    tmp = np.random.permutation(np.arange(len(x)))
    x_tr = x[tmp][:round(train_prop * len(x))]
    y_tr = y[tmp][:round(train_prop * len(x))]
    x_te = x[tmp][-(len(x)-round(train_prop * len(x))):]
    y_te = y[tmp][-(len(x)-round(train_prop * len(x))):]
    return x_tr, x_te, y_tr, y_te


####################################################
# making input function                            #
####################################################
def make_input(documents, max_document_length):
    # tensorflow.contrib.learn.preprocessing 내에 VocabularyProcessor라는 클래스를 이용
    # 모든 문서에 등장하는 단어들에 인덱스를 할당
    # 길이가 다른 문서를 max_document_length로 맞춰주는 역할
    vocab_processor = tf.contrib.learn.preprocessing.VocabularyProcessor(max_document_length)  # 객체 선언
    x = np.array(list(vocab_processor.fit_transform(documents)))
    ### 텐서플로우 vocabulary processor
    # Extract word:id mapping from the object.
    # word to ix 와 유사
    vocab_dict = vocab_processor.vocabulary_._mapping
    # Sort the vocabulary dictionary on the basis of values(id).
    sorted_vocab = sorted(vocab_dict.items(), key=lambda x: x[1])
    # Treat the id's as index into list and create a list of words in the ascending order of id's
    # word with id i goes at index i of the list.
    vocabulary = list(list(zip(*sorted_vocab))[0])
    return x, vocabulary, len(vocab_processor.vocabulary_)

####################################################
# make output function                             #
####################################################
def make_output(points, threshold):
    results = np.zeros((len(points),3))
    for idx, point in enumerate(points):
        results[idx, int(point-1)] = 1
        '''
        if point >= threshold:
            results[idx,1] = 1
        else:
            results[idx,0] = 1
        '''
    return results

####################################################
# check maxlength function                         #
####################################################
def check_maxlength(contents):
    max_document_length = 0
    for document in contents:
        document_length = len(document.split())
        if document_length > max_document_length:
            max_document_length = document_length
    return max_document_length

####################################################
# loading function                                 #
####################################################
def loading_rdata(data_path, eng=True, num=True, punc=False):
    # R에서 title과 contents만 csv로 저장한걸 불러와서 제목과 컨텐츠로 분리
    # write.csv(corpus, data_path, fileEncoding='utf-8', row.names=F)
    try:
        corpus = pd.read_table(data_path,  engine='python', header=None, encoding="utf-8", names=['data', 'label'])
        corpus.dropna(inplace=True)
    except Exception as e:
        print(e)
    corpus = np.array(corpus)
    contents = []
    points = []
    for idx,doc in enumerate(corpus):
        if isNumber(doc[0]) is False:
            content = hangle.normalize(doc[0], english=eng, number=num, punctuation=punc)
            contents.append(content)
            points.append(doc[1])
        if idx % 100000 is 0:
            print('%d docs / %d save' % (idx, len(contents)))
    return contents, points
####################################################
# loading from excel                               #
####################################################
def loading_excel(data_path, eng=True, num=True, punc=False):
    try:
        corpus = pd.read_excel(data_path, usecols=['title','label'], engine='openpyxl')
        corpus.dropna(inplace=True)
    except Exception as e:
        print(e)
    corpus = np.array(corpus)
    contents = []
    points = []
    for idx, doc in enumerate(corpus):
        if isNumber(doc[0]) is False:
            content = hangle.normalize(doc[0], english=eng, number=num, punctuation=punc)
            contents.append(content)
            points.append(doc[1])
        if idx % 100000 is 0:
            print('%d docs / %d save' % (idx, len(contents)))
    return contents, points

def isNumber(s):
  try:
    float(s)
    return True
  except ValueError:
    return False

def select_data(titles, labels):
    size = len(titles)
    lists = [[],[],[],[]]
    for i in range(size):
        if labels[i] == 4:
            labels[i] = 3
        lists[int(labels[i])].append(i)
    lists[2] = lists[2] + lists[2]
    cnt = len(lists[2])
    lists[1] = random.sample(lists[1], cnt)
    lists[3] = random.sample(lists[3], cnt)
    res_titles = []
    res_labels = []
    for idx in range(1, 4):
        for i in range(cnt):
            res_titles.append(titles[lists[idx][i]])
            res_labels.append(labels[lists[idx][i]])
    return res_titles, res_labels