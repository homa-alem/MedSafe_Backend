import nltk
from nltk.probability import ConditionalFreqDist
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
import string
from nltk.corpus import stopwords
import re
from nltk import bigrams
from nltk import trigrams
from nltk.tag.stanford import NERTagger
from nltk.tag.stanford import POSTagger
import xlrd
import xlwt
import os
import math
from math import log
from operator import itemgetter, attrgetter
import random
from textclean.textclean import textclean

data_dir = './../Unique_Data/'
#keyword_dir = './../../Research Data/Keyword_Lists'
train_filename = 'Merged_Final_Unique_Recalls_2007_2011.xls'
test_files = ["unique2007"]
#test_files = ["unique2012","unique2013"]

def selectFeatures(train_set, train_text, k):
    dic = open(data_dir+"best_keywords.txt", "wb")
    # Normalize the text
    small_text = train_text.lower()
    # Replace punctuations (except -) with empty spaces
    regex = re.compile('[%s]' % re.escape('!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~'))
    clean_text = regex.sub(' ',small_text)
    # Tokenize the text
    tokens = nltk.word_tokenize(clean_text)
    # Remove English Stop Words and those words with less than 3 characters
    english_stops = set(stopwords.words('english'))
    words = [word for word in tokens if word not in english_stops and len(word) > 3 and not word.isdigit()]
    # Get rid of tenses for verbs
    #wnl = WordNetLemmatizer()
    #words = [wnl.lemmatize(t, 'v') for t in words]
    print str(len(words))+' words found.'

    # Tagging of the parts of speech
    tagged_words = nltk.pos_tag(words)
    words = [word for (word, tag) in tagged_words if tag in ['NN','JJ','NNS','RB','VB','VBD','VBG','VBN','VBP','VBZ']]
    #words = set(words).intersection(set(unigrams+ bigrams+trigrams));
    # Get the frequency of words
    fdist = nltk.FreqDist(words)
    dictionary = fdist.keys()
    print str(len(dictionary))+' words tagged.'

    l= [];
    # Total number of recalls
    N =  len(train_set);
    NC_list = [(w, u, v) for (w, u,v) in train_set if v == 'Not_Computer'];
    C_list = [(w, u, v) for (w, u,v) in train_set if v != 'Not_Computer'];

    # Number of recalls that are computer-related
    N_1 = len(C_list);
    # Number of recalls that are not computer-related
    N_0 = len(NC_list);

    for w in dictionary:
        A_tc = 0;
        # Number of recalls that have term w
        N1_ = 0;
        # Number of recalls that don't have term w
        N0_ = 0;
        # Number of recalls that have term w and are not computer related
        N10 = 0;
        # Number of recalls that have term w and are computer related
        N11 = 0;
        # Number of recalls that don't have term w and are not computer related
        N00 = 0;
        # Number of recalls that don't have term w and are computer related
        N01 = 0;
        for (number, reason, fault_class) in train_set:
            if (reason.lower().find(w) > -1):
                N1_ = N1_ + 1;
                if (fault_class == 'Not_Computer'):
                    N10 = N10 + 1;
                else:
                    N11 = N11 + 1;
            else:
                N0_ = N0_ + 1;
                if (fault_class == 'Not_Computer'):
                    N00 = N00 + 1;
                else:
                    N01 = N01 + 1;
        # Utility function: Mutual Information to find the best words as features
        if (N11 != 0) and (N1_ != 0) and  (N_1 != 0):
            A_tc = A_tc + (float(N11)/float(N)*math.log(float(N*N11)/float(N1_*N_1),2));
        if (N01 != 0) and (N0_ != 0) and (N_1 != 0):
            A_tc = A_tc + (float(N01)/float(N)*math.log(float(N*N01)/float(N0_*N_1),2));
        if (N10 != 0) and (N1_ != 0) and (N_0 != 0):
            A_tc = A_tc + (float(N10)/float(N)*math.log(float(N*N10)/float(N1_*N_0),2));
        if (N00 != 0) and (N0_ != 0) and (N_0 != 0):
            A_tc = A_tc + (float(N00)/float(N)*math.log(float(N*N00)/float(N0_*N_0),2));
        #print w, A_tc
        # Append to the list
        l.append((A_tc, w));
        dic.write(w + ',' + str(A_tc)+'\n')
    # Get the features
    l.sort();
    #Find the terms with k largest utility function values
    return l[len(l)-k:len(l)-1]

def training(train_set, features):
    # Total number of training recalls
    N =  len(train_set);
    # Total number of terms
    B = len(features)
    Nc = 0;
    Nc_ = 0;

    Ptc = [];
    Ptc_ = [];
    for (s, f) in features:
        N_tc = 1;
        N_tc_ = 1;
        for (number, reason, fault_class) in train_set:
            # Normalize the text
            words = reason.lower()

            if (fault_class == 'Not_Computer'):
                N_tc_ = N_tc_ + words.count(f);
                Nc_ = Nc_ + words.count(f);
            else:
                N_tc = N_tc + words.count(f);
                Nc = Nc + words.count(f);
        Ptc.append((f, N_tc))
        Ptc_.append((f, N_tc_))

    P_tc = {'word':0.0};
    P_tc_ = {'word':0.0};
    for (f,N) in Ptc:
        P_tc[f] = float(N)/(float(Nc)+float(B))

    for (f,N) in Ptc_:
        P_tc_[f] = float(N)/(float(Nc_)+float(B))

    return [P_tc, P_tc_]

def testing(test_set, features, P_tc, P_tc_, Pc, Pc_):
    test_set_labels = []
    for (rownum, number, reason) in test_set:
        testPc = 0;
        testPc_ = 0;
        # Normalize the text
        words = reason.lower()

        for (s,f) in features:
            for i in range(0,words.count(f)):
                testPc = float(testPc) + math.log(float(P_tc[f]),2)
                testPc_ = float(testPc_) + math.log(float(P_tc_[f]),2)

        testPc = float(testPc) + math.log(float(Pc),2);
        testPc_ = float(testPc_) + math.log(float(Pc_),2);

        if (testPc > testPc_):
            fault_class = 'Computer'
        else:
            fault_class = 'Not_Computer'

        test_set_labels.append((rownum, number, reason, fault_class))
    return test_set_labels

def classify():
    # Get the training set of recalls
    train_workbook = xlrd.open_workbook(data_dir+train_filename)
    try:
        worksheet = train_workbook.sheet_by_name('sheet1')
    except:
        worksheet = train_workbook.sheet_by_name('Sheet1')
    num_rows = worksheet.nrows
    num_cols = worksheet.ncols

    train_text = ''
    NC = 0;
    C = 0;
    text_NC = '';
    text_C = '';
    train_set = [];
    # Find the column numbers for Reason and Action
    for j in range(0, num_cols):
        col = worksheet.cell_value(0, j)
        if(col == 'Reason for Recall'):
            Reason_Index = j
        elif(col == 'Action'):
            Action_Index = j
        elif(col == 'Fault Class'):
            Fault_Index = j
    for i in range(1, num_rows):
        number = (worksheet.cell_value(i, 0).strip()).encode('utf-8')
        reason = (worksheet.cell_value(i, Reason_Index).strip()).encode('utf-8')
        action = (worksheet.cell_value(i, Action_Index).strip()).encode('utf-8')
        fault_class = str(worksheet.cell_value(i, Fault_Index).strip()).encode('utf-8')
        train_set.append((number, reason,fault_class))
        train_text = train_text+' '+reason
    print str(len(train_set))
    # Feature Selection
    features = selectFeatures(train_set, train_text, 100)
    dic = open(data_dir+"best_keywords.txt", "rb")
    features = [];
    for line in dic:
        word = line.split(',')[0].strip()
        score = line.split(',')[1].strip()
        features.append((score, word));
    features.sort();
    features = sorted(features, key = itemgetter(0), reverse = True)

    # Total number of recalls in the training set
    N =  len(train_set);
    # Number of recalls that are computer-related
    C_list = [(w, u, v) for (w, u,v) in train_set if v != 'Not_Computer'];
    C = len(C_list);
    # Prior Probabilities
    Pc = float(C)/float(N);
    Pc_ = 1-Pc;

    # Training - Using the highest score features
    [P_tc, P_tc_] = training(train_set, features[1:len(features)/2])


    # Testing
    for filename in test_files:
        test_set = [];
        test_workbook = xlrd.open_workbook(data_dir+filename+'.xls')
        try:
            worksheet = test_workbook.sheet_by_index(0)
        except:
            worksheet = test_workbook.sheet_by_index(0)
        num_rows = worksheet.nrows
        num_cols = worksheet.ncols

        newbook = xlwt.Workbook("iso-8859-2")
        newsheet = newbook.add_sheet('Sheet1', cell_overwrite_ok = True)

        # Find the column numbers for Reason and Action
        for j in range(0, num_cols):
            col = worksheet.cell_value(0, j)
            if(col == 'Reason for Recall'):
                Reason_Index = j
            elif(col == 'Action'):
                Action_Index = j
            elif(col == 'Fault Class'):
                Fault_Index = j
        for i in range(1, num_rows):
            number = (worksheet.cell_value(i, 0).strip()).encode('utf-8')
            reason = (worksheet.cell_value(i, Reason_Index).strip()).encode('utf-8')
            test_set.append((i, number, reason))
        print 'Testing: '+filename
        print str(len(test_set))
        # Testing  - Using the highest score features
        test_set_labels = testing(test_set, features[1:len(features)/2], P_tc, P_tc_, Pc, Pc_)

        for k in range(0,num_cols):
            newsheet.write(0, k, worksheet.cell_value(0, k));
        newsheet.write(0, k+1, 'Fault_Class');

        test_set_labels = sorted(test_set_labels, key = itemgetter(3), reverse = True)
        for (i, number, reason, fault_class) in test_set_labels:
            for k in range(0,num_cols):
                newsheet.write(i, k, worksheet.cell_value(i, k));
            newsheet.write(i, k+1, fault_class);

        newbook.save(data_dir+str(filename)+'_classified.xls')

    dic.close();

if(__name__ == '__main__'):
    classify()
