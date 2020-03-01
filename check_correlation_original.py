#!/usr/bin/env python
# coding: utf-8

# Check correlation using original paper method
# Paper link: https://ears2018.github.io/ears18-bountouridis.pdf?fbclid=IwAR1kTjhBLIibieg_OyqxW-IQURTodwiK26lKhs_Uw-77d1QtKcBSqCa1pPY

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import xlrd
import xlwt
import re
import os
import datetime
import random as rng

ngram_db_file = "ngram_db.xls"
news_db_file = "articles.xls"
result_file = "result_original.csv"

news_groups = 10
news_per_group = 10

# For starter, we will only check unigrams
# Load unigram db
unigram_dict = {}
if os.path.isfile(ngram_db_file):
    ngram_db = xlrd.open_workbook(ngram_db_file)

    unigram_db = ngram_db.sheet_by_index(0)
    for i in range(unigram_db.nrows):
        key = unigram_db.cell(i, 0).value
        tf = int(unigram_db.cell(i, 1).value) #term frequency
        df = int(unigram_db.cell(i, 2).value) #doc frequency
        unigram_dict[key] = [tf, df]

# Load news articles
news_count = 0
news_list = []
all_news_db = xlrd.open_workbook(news_db_file)
sheet = all_news_db.sheet_by_index(0)
rows = sheet.nrows
# print (rows)
for row in range(rows):
    # Headline in column 0, Details in column 1
    source = sheet.cell(row, 0).value
    headline = sheet.cell(row, 1).value
    body = sheet.cell(row, 2).value
    news_list.append([source, headline, body])
    # print(headline)

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
# Calculation method
# matrix = N / D1 * D2
# N = n_ngrams * c_ngrams
# D1 = sqrt(n_ngrams * n_ngrams)
# D2 = sqrt(c_ngrams * c_ngrams)

correlation_matrix = np.zeros((news_count, news_count))

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
        
        case  = 1 # Checking two different methods, case 1 is from the original paper
        if case == 1:
            N = 0
            D1 = 0
            D2 = 0
            for ng in merged_ngrams:  
                if ng in n_ngrams and ng in c_ngrams:          
                    N += (n_ngrams[ng] * c_ngrams[ng])
                if ng in n_ngrams:
                    D1 += (n_ngrams[ng] * n_ngrams[ng])
                if ng in c_ngrams:
                    D2 += (c_ngrams[ng] * c_ngrams[ng])
        else:
            N = 0
            D1 = 0
            D2 = 0
            for ng in common_ngrams:            
                N += (n_ngrams[ng] * c_ngrams[ng])   
                D1 += (n_ngrams[ng] * n_ngrams[ng])
                D2 += (c_ngrams[ng] * c_ngrams[ng])
        
        correlation = 0        
        if D1 != 0 and D2 != 0:
            correlation = N / (D1 * D2)

        correlation_matrix[n, c] = correlation
        correlation_matrix[c, n] = correlation

print(correlation_matrix)

correlation_matrix_by_cliques = np.zeros((news_count, news_count))
find_cliques = True
cutoff = 2.0 # From the paper
if find_cliques:
    import networkx as nx    
    
    matrix  = [[0 if j < cutoff else j for j in i] for i in correlation_matrix]
    # print (correlation_matrix)
    # Convert to graph
    M = np.matrix(matrix)
    G = nx.from_numpy_matrix(M)    
    
    # Plot to verify
    plot_network = True
    if plot_network:
        pos = nx.spiral_layout(G) # All layouts at https://networkx.github.io/documentation/stable/reference/drawing.html#module-networkx.drawing.layout
        nx.draw_networkx(G, pos, node_color = '#2020A0', edge_color = '#468646', font_color = '#ffffff')
        plt.axis("off")
        plt.show()
    
    # Find cliques
    cliques = list(nx.find_cliques(G))
    # print (cliques)

    # Calculate accuracy using clique technique
    # cn = list(nx.cliques_containing_node(G, nodes=1, cliques=c))
    for n in range(news_count):
        ncliques = [c for c in cliques if n in c]        
        flatten = [j for i in ncliques for j in i]     
        related = list(dict.fromkeys(flatten)) # Remove duplicates

        for r in related:
            correlation_matrix_by_cliques[n, r] = 1
            correlation_matrix_by_cliques[r, n] = 1


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
        ax.imshow(correlation_matrix)
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
    for i in range(10):        
        for j in range(10):
            for k in range(10):
                actual_correlation[i * 10 + j, i * 10 + k] = 1

    # Plot actual correlation
    plot_correlation(actual_correlation, "Actual news correlation matrix")


    # Simple method
    # ============================================================================
    # Pre-process the correlation matrix
    processed = preprocess_correlation_matrix(correlation_matrix)

    # Plot
    title = "Inferred news correlation matrix  [Method from paper]"
    if filter_out_terms_with_low_tfidf:
        title += " (term filtered)"

    plot_correlation(processed, title)

    # Find accuracy    
    [accuracy, fp, fn] = find_accuracy(actual_correlation, processed)
    print("Method from paper")
    print ("Accuracy: " + str(accuracy) + "%")
    print ("False positives: " + str(fp) + "%")
    print ("False negatives: " + str(fn) + "%")

    # Clique method
    # ============================================================================
    if find_cliques:    
        # Does not require any pre-processing
        processed = correlation_matrix_by_cliques

        # Plot
        title = "News correlation matrix  [using cliques, cutoff = " + str(cutoff) + "]"
        if filter_out_terms_with_low_tfidf:
            title += " (term filtered)"

        plot_correlation(processed, title)

        # Find accuracy    
        [accuracy, fp, fn] = find_accuracy(actual_correlation, processed)
        print("Method from paper (using cliques)")
        print ("Accuracy: " + str(accuracy) + "%")
        print ("False positives: " + str(fp) + "%")
        print ("False negatives: " + str(fn) + "%")


# Test and save ==================================================================
if os.path.isfile(result_file):
    os.remove(result_file)
np.savetxt(result_file, correlation_matrix, delimiter=",")

# To test if the process is working
test = False
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





