#!/usr/bin/env python
# coding: utf-8

# This script process the source excel file and updates the ngram database

import xlrd
import xlwt
import re
import os
import datetime

# infile = "Prothom_Alo.xls"
# outfile = "ngram_db.xls"

# For our test
infile = "articles.xls"
outfile = "ngram_db.xls"

unigram_dict = {}
bigram_dict = {}
trigram_dict = {}
checked_list = []

# Load existing ngram ngram_db and temporarily store into a dictionary 
if os.path.isfile(outfile):
    ngram_db = xlrd.open_workbook(outfile)

    unigram_db = ngram_db.sheet_by_index(0)
    for i in range(unigram_db.nrows):
        key = unigram_db.cell(i, 0).value
        tf = int(unigram_db.cell(i, 1).value) #term frequency
        df = int(unigram_db.cell(i, 2).value) #doc frequency
        unigram_dict[key] = [tf, df]

    bigram_db = ngram_db.sheet_by_index(1)
    for i in range(bigram_db.nrows):
        key =bigram_db.cell(i, 0).value
        tf = int(bigram_db.cell(i, 1).value) #term frequency
        df = int(bigram_db.cell(i, 2).value) #doc frequency
        bigram_dict[key] = [tf, df]

    trigram_db = ngram_db.sheet_by_index(2)
    for i in range(trigram_db.nrows):
        key =trigram_db.cell(i, 0).value
        tf = int(trigram_db.cell(i, 1).value) #term frequency
        df = int(trigram_db.cell(i, 2).value) #doc frequency
        trigram_dict[key] = [tf, df]

    # news_headline already done news_item
    checked_db = ngram_db.sheet_by_index(3)    
    for i in range(checked_db.nrows):
        # date = checked_db.cell(i, 0).value         # ideally date should also be added
        source = checked_db.cell(i, 0).value
        headline = checked_db.cell(i, 1).value
        checked_list.append([source, headline])


# Process input file
workbook = xlrd.open_workbook(infile)
news_items = workbook.sheet_by_index(0)

for i in range(news_items.nrows):
    # news_date = news_items.cell(i,0).value
    news_source = news_items.cell(i,0).value
    news_headline = news_items.cell(i,1).value
    news_item = news_items.cell(i,2).value    

    # If news_item is already process then continue
    if [news_source, news_headline] in checked_list:
        continue

    checked_list.append([news_source, news_headline]) #new news
    
    # Make three lists with one, two and three words    
    unigram_list = re.split('\s|\)|\(|:|\।|\।|, ', news_item)
    unigram_list = list(filter(None, unigram_list))
    bigram_list=[]
    trigram_list=[]

    for j in range(1, len(unigram_list) ):
        bigram_list.append(unigram_list[j-1] + " " + unigram_list[j])
        
    for j in range(2, len(unigram_list) ):
        trigram_list.append(unigram_list[j-2] + " " + unigram_list[j-1] + " " + unigram_list[j])
        
    # Update unigram dictionary
    updated_ngrams = {}  
    for ngram in (unigram_list):
        if ngram in unigram_dict:
            unigram_dict[ngram][0] += 1 # Update tf
            updated_ngrams[ngram] = True
        else: # New ngram
            unigram_dict[ngram] = [1,1]

    for ngram in updated_ngrams.keys():
        unigram_dict[ngram][1] += 1 # Update df
            
    # Update bigram dictionary  
    updated_ngrams = {}  
    for ngram in (bigram_list):
        if ngram in bigram_dict:
            bigram_dict[ngram][0] += 1 # Update tf
            updated_ngrams[ngram] = True
        else: # New ngram
            bigram_dict[ngram] = [1,1]

    for ngram in updated_ngrams.keys():
        bigram_dict[ngram][1] += 1 # Update df
    
    # Update trigram dictionary  
    updated_ngrams = {}  
    for ngram in (trigram_list):
        if ngram in trigram_dict:
            trigram_dict[ngram][0] += 1 # Update tf
            updated_ngrams[ngram] = True
        else: # New ngram
            trigram_dict[ngram] = [1,1]

    for ngram in updated_ngrams.keys():
        trigram_dict[ngram][1] += 1 # Update df

        
# Store into a ngram_db
workbook = xlwt.Workbook()
sheet_unigram = workbook.add_sheet("unigram")
sheet_bigram = workbook.add_sheet("bigram")
sheet_trigram = workbook.add_sheet("trigram")
sheet_checked = workbook.add_sheet("checked")
row = 0
column = 0

for key, [tf, df] in unigram_dict.items():
    if(row > 65530): # This is a bad hack, should use mysql for saving all data
        row = 0
        column = column + 2

    sheet_unigram.write(row, column, key)
    sheet_unigram.write(row, column + 1, tf)
    sheet_unigram.write(row, column + 2, df)
    row += 1

row = 0
column = 0
for key, cnt in bigram_dict.items():
    if(row > 65530):
        row = 0
        column = column + 2

    sheet_bigram.write(row, column, key)
    sheet_bigram.write(row, column + 1, tf)
    sheet_bigram.write(row, column + 2, df)
    row += 1

row = 0
column = 0
for key, cnt in trigram_dict.items():
    if(row > 65530):
        row = 0
        column = column + 2

    sheet_trigram.write(row, column, key)
    sheet_trigram.write(row, column + 1, tf)
    sheet_trigram.write(row, column + 2, df)
    row += 1

row = 0
column = 0
for [source, headline] in checked_list:
    if(row > 65530):
        row = 0
        column = column + 2
    sheet_checked.write(row, column, source)
    sheet_checked.write(row, column + 1, headline)
    row += 1

if os.path.isfile(outfile):
    os.remove(outfile)

workbook.save(outfile)

