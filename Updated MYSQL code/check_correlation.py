#!/usr/bin/env python
# coding: utf-8

import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import xlrd
import xlwt
import re
import os
import datetime
import random as rng
import mysql.connector
import json

mydb=mysql.connector.connect(
        host="10.12.33.184",
        port=3306,
        user="cste2015-16",
        passwd="nstu101",
        database="cste2015-16"
        )
mycursor=mydb.cursor()

news_groups = 10
news_per_group = 10

# For starter, we will only check unigrams
# Load unigram db
unigram_dict = {}
# =============================================================================
# if os.path.isfile(ngram_db_file):
#     ngram_db = xlrd.open_workbook(ngram_db_file)
# 
#     unigram_db = ngram_db.sheet_by_index(0)
#     for i in range(unigram_db.nrows):
#         key = unigram_db.cell(i, 0).value
#         tf = int(unigram_db.cell(i, 1).value) #term frequency
#         df = int(unigram_db.cell(i, 2).value) #doc frequency
#         unigram_dict[key] = [tf, df]
# =============================================================================
mycursor.execute("SELECT COUNT(*) FROM uni_gram")
rows=mycursor.fetchone()
nrows=int(rows[0])
#unigram_db = ngram_db.sheet_by_index(0)
for i in range(nrows):
    sql="SELECT * FROM uni_gram LIMIT %s,%s"
    val=(i,1)
    mycursor.execute(sql,val)
    unigram_db=mycursor.fetchall()
    key = unigram_db[0][0]
    tf = int(unigram_db[0][1]) #term frequency
    df = int(unigram_db[0][2]) #doc frequency
    #updated[key]=True
    unigram_dict[key] = [tf, df]
    
# Load news articles
news_count = 0
news_list = []
# =============================================================================
# all_news_db = xlrd.open_workbook(news_db_file)
# sheet = all_news_db.sheet_by_index(0)
# rows = sheet.nrows
# # print (rows)
# for row in range(rows):
#     # Headline in column 0, Details in column 1
#     source = sheet.cell(row, 0).value
#     headline = sheet.cell(row, 1).value
#     body = sheet.cell(row, 2).value
#     news_list.append([source, headline, body])
# =============================================================================
    # print(headline)
mycursor.execute("SELECT COUNT(*) FROM articles")
rows=mycursor.fetchone()
nrows=int(rows[0])
for i in range(nrows):
    sql="SELECT * FROM articles LIMIT %s,%s"
    val=(i,1)
    mycursor.execute(sql,val)
    news_items=mycursor.fetchall()
    # news_date = news_items.cell(i,0).value
    source = news_items[0][0]
    headline = news_items[0][1]
    body = news_items[0][2]
    news_list.append([source, headline, body])
    
news_count = len(news_list)
news_processed = []
filter_out_terms_with_low_tfidf = False

for [source, headline, body] in news_list:
    unigrams = re.split('\s|\)|\(|:|\।|\।|, ', body)
    unigrams = list(filter(None, unigrams))
    unigrams_count = len(unigrams)

    tf_dict = {}
    tfidf_dict = {}
    tfidf_dict = {}
    tfidf_dict_filtered = {}
    tfidfs = [] # For calculating mean
    # tf = count of a term in a doc / number of terms in the doc
    
    for ngram in unigrams:
        if ngram in tf_dict:
            tf_dict[ngram] += 1
        else:
            tf_dict[ngram] = 1

    for ngram in tf_dict.keys():
        tf = tf_dict[ngram] / unigrams_count
        df = 1
        if ngram in unigram_dict.keys():
            df = unigram_dict[ngram][1]
        idf = np.log(news_count/df)
        tfidf = tf * idf
        tfidf_dict[ngram] = tfidf
        tfidfs.append(tfidf)
    
    if filter_out_terms_with_low_tfidf:
        tfidf_mean = np.mean(tfidfs)
        # Remove all terms with tfidf less than mean
        for ngram, tfidf in tfidf_dict.items():
            if tfidf > tfidf_mean:
                tfidf_dict_filtered[ngram] = tfidf
    else:
        for ngram, tfidf in tfidf_dict.items():
            tfidf_dict_filtered[ngram] = tfidf

    # del tfidf_dict
    news_processed.append([source, headline, tfidf_dict_filtered])

# print (news_processed)
print(len(news_processed))

# Now create the correlation matrix
correlation_matrix1 = np.zeros((news_count, news_count))
correlation_matrix2 = np.zeros((news_count, news_count)) # Using second method
correlation_matrix3 = np.zeros((news_count, news_count)) # Using third method

for n in range(news_count):
    n_headline = news_processed[n][1]
    # print (headline)
    n_ngrams = news_processed[n][2]

    for c in range (n + 1, news_count):
        c_headline = news_processed[c][1]    
        c_ngrams = news_processed[c][2]

        merged_ngrams = list(n_ngrams.keys()) + list(c_ngrams.keys())
        merged_ngrams = list(dict.fromkeys(merged_ngrams))
        common_ngrams = []

        for ngram in merged_ngrams:
            if (ngram in n_ngrams) and (ngram in c_ngrams):
                common_ngrams.append(ngram)

        correlation1 = len(common_ngrams) / len(merged_ngrams)
        correlation_matrix1[n, c] = correlation1
        correlation_matrix1[c, n] = correlation1

        # Method 2
        correlation2 = 0.0
        for ngram in common_ngrams:
            correlation2 += (n_ngrams[ngram] * c_ngrams[ngram])
        correlation_matrix2[n, c] = correlation2
        correlation_matrix2[c, n] = correlation2

        # Method 3 
        correlation3 = math.exp(correlation1) * correlation2
        correlation_matrix3[n, c] = correlation3
        correlation_matrix3[c, n] = correlation3

# print(correlation_matrix1)
# print(correlation_matrix2)
# print(correlation_matrix3)

plot = True
if plot == True:
    news_ids = list(range(1, news_count + 1))

    def preprocess_correlation_matrix(correlation_matrix):
        # Pre-process the correlation matrix
        processed = np.zeros((news_count, news_count))
        for r in range(news_count):
            cor_dict = {}
            for i in range(news_count):
                cor_dict[i] = correlation_matrix[i, r]
            cor_dict = {k: v for k, v in sorted(cor_dict.items(), key=lambda item: item[1], reverse=True)}
            
            i = 0
            for h in cor_dict.keys():
                processed[h, r] = 1            
                i += 1
                if i >= 9:
                    break
            processed[r, r] = 1
        return processed

    def plot_correlation(correlation_matrix, title): 
        fig, ax = plt.subplots()
        im = ax.imshow(correlation_matrix)
        ax.set_title(title)
        fig.tight_layout()
        plt.show()

    def find_accuracy(actual, inferred):
        # matched = 0
        not_matched = 0
        false_positives = 0
        false_negatives = 0
        for i in range(news_count):
            for j in range(news_count):
                # if actual[i, j] == inferred[i, j]:
                #     matched += 1
                if actual[i, j] != inferred[i, j]:
                    not_matched += 1
                if actual[i, j] == 0 and inferred[i, j] == 1:
                    false_positives += 1    
                if actual[i, j] == 1 and inferred[i, j] == 0:
                    false_negatives += 1

        # Ideally number of false positives and false negatives will be equal as the error is divided equally
        # matched % + false positives % + false negatives % = 100%

        # Wrong methods           
        # accuracy = (matched / (news_count * news_count)) * 100
        # fp_percentage = (false_positives / (news_count * news_count)) * 100
        # fn_percentage = (false_negatives / (news_count * news_count)) * 100

        # The thing is, the number of mismatches cannot exceed the value 2 * (news_groups * (news_per_group * news_per_group))
        # Here multiplying with 2 is important otherwise, accuracy can be negative for too many mismatches

        possible_matches = 2 * (news_groups * (news_per_group * news_per_group))
        accuracy = ((possible_matches - not_matched) / possible_matches) * 100
        fp_percentage = (false_positives / possible_matches) * 100
        fn_percentage = (false_negatives / possible_matches) * 100
        
        return [accuracy, fp_percentage, fn_percentage]


    # Actual correlation
    actual_correlation = np.zeros((news_count, news_count))
    for i in range(news_groups):        
        for j in range(news_per_group):
            for k in range(news_per_group):
                actual_correlation[i * news_per_group + j, i * news_per_group + k] = 1

    # Plot actual correlation
    plot_correlation(actual_correlation, "Actual news correlation matrix")


    # Method 1
    # ============================================================================
    # Pre-process the correlation matrix
    processed = preprocess_correlation_matrix(correlation_matrix1)

    # Plot
    title = "Inferred news correlation matrix  [Method 1]"
    if filter_out_terms_with_low_tfidf:
        title += " (term filtered)"

    plot_correlation(processed, title)

    # Find accuracy    
    [accuracy, fp, fn] = find_accuracy(actual_correlation, processed)
    print ("Method 1 accuracy: " + str(accuracy) + "%")
    print ("Method 1 false positives: " + str(fp) + "%")
    print ("Method 1 false negatives: " + str(fn) + "%")
    print ("")

   # Method 2
    # ============================================================================
    # Pre-process the correlation matrix
    processed = preprocess_correlation_matrix(correlation_matrix2)

    # Plot
    title = "Inferred news correlation matrix  [Method 2]"
    if filter_out_terms_with_low_tfidf:
        title += " (term filtered)"

    plot_correlation(processed, title)

    # Find accuracy    
    [accuracy, fp, fn] = find_accuracy(actual_correlation, processed)
    print ("Method 2 accuracy " + str(accuracy) + "%")
    print ("Method 2 false positives: " + str(fp) + "%")
    print ("Method 2 false negatives: " + str(fn) + "%")
    print ("")

    # Method 1
    # ============================================================================
    # Pre-process the correlation matrix
    processed = preprocess_correlation_matrix(correlation_matrix3)

    # Plot
    title = "Inferred news correlation matrix  [Method 3]"
    if filter_out_terms_with_low_tfidf:
        title += " (term filtered)"

    plot_correlation(processed, title)

    # Find accuracy    
    [accuracy, fp, fn] = find_accuracy(actual_correlation, processed)
    print ("Method 3 accuracy: " + str(accuracy) + "%")
    print ("Method 3 false positives: " + str(fp) + "%")
    print ("Method 3 false negatives: " + str(fn) + "%")
    print ("")
        

# Test and save ==================================================================
correlation_matrix = correlation_matrix2 # Best accuracy

create_table=True
if create_table:
    mycursor.execute("CREATE TABLE IF NOT EXISTS `result` (row int,column_0 FLOAT)")
    i=0
    while (i < news_count):
        #sql="ALTER TABLE 'result(original)'  ADD %s FLOAT NULL  AFTER %s"
        sql="ALTER TABLE `result` ADD column_%s FLOAT NULL AFTER column_%s"
        val=(i+1,i)
        mycursor.execute(sql,val)
        i+=1
        
mycursor.execute("DELETE FROM `result`")
for i in range(news_count):
    for j in range(news_count):
        val=float(correlation_matrix[i][j])
        sql1="INSERT INTO `result` (row, column_%s) VALUES (%s, %s)"
        val1=(j,i,val)
        sql2="UPDATE `result` SET column_%s = %s WHERE row = %s"
        val2=(j,val,i)
        if j==0:
            mycursor.execute(sql1,val1)
            
        else:
            mycursor.execute(sql2,val2)
# =============================================================================
# if os.path.isfile(result_file):
#     os.remove(result_file)
# np.savetxt(result_file, correlation_matrix, delimiter=",")
# =============================================================================
mydb.commit()
# To test if the process is working
test = True
if test:    
    print ('Taking a random news article:')
    r = rng.randint(0, news_count - 1)    
    news = news_processed[r]
    headline = news[1]
    print(headline)
    cor_dict = {}
    for i in range(news_count):
        cor_dict[i] = correlation_matrix[i, r]
    cor_dict = {k: v for k, v in sorted(cor_dict.items(), key=lambda item: item[1], reverse=True)}
    print(cor_dict.keys())

    print('Top 9 related news:')
    i = 0
    for h in cor_dict.keys():
        print(news_processed[h][1])
        i += 1
        if i >= 9:
            break

