# Connection Script
import mysql.connector
from mysql.connector import errorcode

hostname = 'localhost'
password = 'Bokunoheroacademia@1'
db = 'bristol_events_db'
username = 'root'

# connects db 
def getConnection():
    try:
        conn = mysql.connector.connect(host=hostname,
                                user=username,
                                password=password,
                                database=db)

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('Username or Password is not working/incorrect')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('Database does not exist')
        else:  
            print(err)
    else: # Will execute if connection is successful
        return conn    