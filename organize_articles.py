#!/usr/bin/env python
# coding: utf-8

# Organize all articles in a single file

import xlrd
import xlwt
import re
import os
import datetime

outfile = "articles.xls"
sheets = 10
randomize = False
news_list = []

all_news_db = xlrd.open_workbook("collected_news.xls")

for s in range(sheets):
    sheet = all_news_db.sheet_by_index(s)
    rows = sheet.nrows
    print (rows)
    for row in range(rows):
        # Headline in column 1, Details in column 2
        source = sheet.cell(row, 0).value
        headline = sheet.cell(row, 1).value
        body = sheet.cell(row, 2).value
        news_list.append([source, headline, body])

# if randomize:
    # Do nothing now
    # Will think about it later

# Save
workbook = xlwt.Workbook()
sheet = workbook.add_sheet("articles")
row = 0
for [source, headline, body] in news_list:    
    sheet.write(row, 0, source)
    sheet.write(row, 1, headline)
    sheet.write(row, 2, body)
    row += 1

if os.path.isfile(outfile):
    os.remove(outfile)

workbook.save(outfile)