# Student Name: Alvin Vellappallil
# Student ID: 24028338

# Connection Script
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

hostname = os.getenv('DB_HOSTNAME')
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
db = os.getenv('DB_NAME')

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