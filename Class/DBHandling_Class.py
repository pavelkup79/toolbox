#!/usr/bin/python

import cx_Oracle
import pprint
import csv

db = cx_Oracle.connect('ABPAPP1/ABPAPP1@indlnqw879:1521/VIVDB307')
cursor = db.cursor()
sql = "SELECT customer_id FROM customer"
cursor.execute(sql)
#data = cursor.fetchall()
#col_names = []
#for i in range(0, len(cursor.description)):
#    col_names.append(cursor.description[i][0])
#pp = pprint.PrettyPrinter(width=1024)
#pp.pprint(col_names)
#pp.pprint(data)
#cursor.close()
#db.close()

with open("myfile.csv", "w") as outfile:
    writer = csv.writer(outfile, delimiter = ";")
    for row in cursor:
        writer.writerow(row)
db.close()