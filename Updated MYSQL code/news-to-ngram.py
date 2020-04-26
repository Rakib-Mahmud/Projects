#!/usr/bin/env python
# coding: utf-8

# This script process the source excel file and updates the ngram database
import re
import mysql.connector

mydb=mysql.connector.connect(
        host="192.168.0.102",
        #host="10.12.33.184",
        port=3306,
        user="cste2015-16",
        passwd="nstu101",
        database="cste2015-16"
        )
mycursor=mydb.cursor()
create_table=True
if create_table:
    mycursor.execute("CREATE TABLE IF NOT EXISTS `uni_gram` (Word VARCHAR(200),TF INT,DF INT)COLLATE utf8mb4_unicode_ci")
    mycursor.execute("CREATE TABLE IF NOT EXISTS `bi_gram` (Word VARCHAR(200),TF INT,DF INT)COLLATE utf8mb4_unicode_ci")
    mycursor.execute("CREATE TABLE IF NOT EXISTS `tri_gram` (Word VARCHAR(200),TF INT,DF INT)COLLATE utf8mb4_unicode_ci")
    mycursor.execute("CREATE TABLE IF NOT EXISTS `newspaper_processed` (Source VARCHAR(30),Headline VARCHAR(200),PRIMARY KEY(Source,Headline))COLLATE utf8mb4_unicode_ci")
# infile = "Prothom_Alo.xls"
# outfile = "ngram_db.xls"

# For our test
unigram_dict = {}
bigram_dict = {}
trigram_dict = {}
checked_list = []
updated={}
# Load existing ngram ngram_db and temporarily store into a dictionary 

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
    updated[key]=True
    unigram_dict[key] = [tf, df]
mycursor.execute("SELECT COUNT(*) FROM bi_gram")
rows=mycursor.fetchone()
nrows=int(rows[0])
#bigram_db = ngram_db.sheet_by_index(1)
for i in range(nrows):
    sql="SELECT * FROM bi_gram LIMIT %s,%s"
    val=(i,1)
    mycursor.execute(sql,val)
    bigram_db=mycursor.fetchall()
    key =bigram_db[0][0]
    tf = int(bigram_db[0][1]) #term frequency
    df = int(bigram_db[0][2]) #doc frequency
    updated[key]=True
    bigram_dict[key] = [tf, df]
mycursor.execute("SELECT COUNT(*) FROM tri_gram")
rows=mycursor.fetchone()
nrows=int(rows[0])
#trigram_db = ngram_db.sheet_by_index(2)
for i in range(nrows):
    sql="SELECT * FROM tri_gram LIMIT %s,%s"
    val=(i,1)
    mycursor.execute(sql,val)
    trigram_db=mycursor.fetchall()
    key =trigram_db[0][0]
    tf = int(trigram_db[0][1]) #term frequency
    df = int(trigram_db[0][2]) #doc frequency
    updated[key]=True
    trigram_dict[key] = [tf, df]

# news_headline already done news_item
mycursor.execute("SELECT COUNT(*) FROM newspaper_processed")
rows=mycursor.fetchone()
nrows=int(rows[0])
#checked_db = ngram_db.sheet_by_index(3)    
for i in range(nrows):
    # date = checked_db.cell(i, 0).value         # ideally date should also be added
    sql="SELECT * FROM newspaper_processed LIMIT %s,%s"
    val=(i,1)
    mycursor.execute(sql,val)
    checked_db=mycursor.fetchall()
    source = checked_db[0][0]
    headline = checked_db[0][1]
    checked_list.append([source, headline])


# Process input file
c=0
mycursor.execute("SELECT COUNT(*) FROM articles")
rows=mycursor.fetchone()
nrows=int(rows[0])
for i in range(nrows):
    sql="SELECT * FROM articles LIMIT %s,%s"
    val=(i,1)
    mycursor.execute(sql,val)
    news_items=mycursor.fetchall()
    # news_date = news_items.cell(i,0).value
    news_source = news_items[0][0]
    news_headline = news_items[0][1]
    news_item = news_items[0][2]

    # If news_item is already process then continue
    if [news_source, news_headline] in checked_list:
         continue

    checked_list.append([news_source, news_headline]) #new news
    
    # Make three lists with one, two and three words    
    #unigram_list = re.split('\s|\)|\(|:|\।|\।|, |\'|-|_', news_item)
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
        #if unigram_dict.get(ngram) != None:
            unigram_dict[ngram][0]=int(unigram_dict[ngram][0]) + 1 # Update tf
            updated_ngrams[ngram] = True
            c+=1
            #updated[ngram]=True
        else: # New ngram
            unigram_dict[ngram] = [1,1]

    for ngram in updated_ngrams.keys():
        unigram_dict[ngram][1]=int(unigram_dict[ngram][1]) + 1 # Update df
            
    # Update bigram dictionary  
    updated_ngrams = {}  
    for ngram in (bigram_list):
        #if ngram in bigram_dict:
        if bigram_dict.get(ngram) != None:
            bigram_dict[ngram][0] += 1 # Update tf
            updated_ngrams[ngram] = True
            #updated[ngram]=True
        else: # New ngram
            bigram_dict[ngram] = [1,1]

    for ngram in updated_ngrams.keys():
        bigram_dict[ngram][1] += 1 # Update df
    
    # Update trigram dictionary  
    updated_ngrams = {}  
    for ngram in (trigram_list):
        #if ngram in trigram_dict:
        if trigram_dict.get(ngram) != None:
            trigram_dict[ngram][0] += 1 # Update tf
            updated_ngrams[ngram] = True
            #updated[ngram]=True
        else: # New ngram
            trigram_dict[ngram] = [1,1]

    for ngram in updated_ngrams.keys():
        trigram_dict[ngram][1] += 1 # Update df

        
   # Store into a ngram_db
for key, values in unigram_dict.items():
    try:
       sql2="INSERT INTO uni_gram (Word,TF,DF) VALUES (%s,%s,%s)"
       sql1="UPDATE uni_gram SET TF = %s, DF = %s WHERE Word = %s"
       tf=values[0]
       df=values[1]
       val1=(tf,df,key)
       val2=(key,tf,df)
       if key in updated:
       #if updated.get(key) != None:
           mycursor.execute(sql1,val1)
       else:    
           mycursor.execute(sql2,val2)
    except:
       print("Duplicate.")
       print(key)
       
for key, values in bigram_dict.items():
    try: 
       sql2="INSERT INTO bi_gram (Word,TF,DF) VALUES (%s,%s,%s)"
       sql1="UPDATE bi_gram SET TF = %s, DF = %s WHERE Word = %s"
       tf=values[0]
       df=values[1]
       val1=(tf,df,key)
       val2=(key,tf,df)
       if updated.get(key) != None:
           mycursor.execute(sql1,val1)
       else:    
           mycursor.execute(sql2,val2)
    except:
        print("Duplicate..")

for key, values in trigram_dict.items():
    try: 
       sql2="INSERT INTO tri_gram (Word,TF,DF) VALUES (%s,%s,%s)"
       sql1="UPDATE tri_gram SET TF = %s, DF = %s WHERE Word = %s"
       tf=values[0]
       df=values[1]
       val1=(tf,df,key)
       val2=(key,tf,df)
       if updated.get(key) != None:
           mycursor.execute(sql1,val1)
       else:    
           mycursor.execute(sql2,val2)
    except:
        print("Duplicate...")

for [source, headline] in checked_list:
     try:
         sql="INSERT INTO newspaper_processed (Source,Headline) VALUES (%s,%s)"
         val=(source,headline)
         mycursor.execute(sql,val)
     except:
        print("Dup")

mydb.commit()
