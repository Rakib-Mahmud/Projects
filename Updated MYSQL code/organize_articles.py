#!/usr/bin/env python
# coding: utf-8

# Organize all articles in a single file

import xlrd
import xlwt
import re
import os
import mysql.connector
import datetime

mydb=mysql.connector.connect(
        host="10.12.33.184",
        port=3306,
        user="cste2015-16",
        passwd="nstu101",
        database="cste2015-16"
        )
mycursor=mydb.cursor()

create_table=True
if create_table:
    mycursor.execute("CREATE TABLE IF NOT EXISTS `articles` (Source VARCHAR(200),Headline VARCHAR(200),Content TEXT)COLLATE utf8mb4_unicode_ci")
#outfile = "articles.xls"
sheets = 10
randomize = False
news_list = []


for s in range(sheets):
    sheet = all_news_db.sheet_by_index(s)
    rows = sheet.nrows
    print (rows)
    for row in range(rows):
        # Headline in column 1, Details in column 2
        source = sheet.cell(row, 0).value
        headline = sheet.cell(row, 1).value
        body = sheet.cell(row, 2).value
#        news_list.append([source, headline, body])
        sql="INSERT INTO articles (Source,Headline,Content) VALUES (%s,%s,%s)"
        values=(source,headline,body)
        mycursor.execute(sql,values)
        
mydb.commit()
# if randomize:
    # Do nothing now
    # Will think about it later

# Save
# =============================================================================
# workbook = xlwt.Workbook()
# sheet = workbook.add_sheet("articles")
# row = 0
# for [source, headline, body] in news_list:    
#     sheet.write(row, 0, source)
#     sheet.write(row, 1, headline)
#     sheet.write(row, 2, body)
#     row += 1
# 
# if os.path.isfile(outfile):
#     os.remove(outfile)
# 
# workbook.save(outfile)
# =============================================================================
