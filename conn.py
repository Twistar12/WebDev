import mysql.connector, dbfunc, sys
from mysql.connector import errorcode

conn = dbfunc.getConnection()

if conn != None:
    if conn.is_connected(): # Reports whethter MySQL connection has been established 
        print('MySQL Connection has been established')
        dbcursor = conn.cursor() # Creates cursor object to run queries and execute statements
        # DB queries here

        # End of queries
        dbcursor.close()
        conn.close()
    else:
        print('MySQL Connection Error')
else:
    print('DBFunc Error, check dbfunc.py')