# import os
# os.system("sudo kill `sudo lsof -t -i:9001`")

import MySQLdb

connection = MySQLdb.Connect(host='**', user='**', passwd='**', db='**')
cursor = connection.cursor()
query = "LOAD DATA INFILE '/database/database.sql'"
cursor.execute( query )
connection.commit()