from flask import Flask
from time import time
from random import randint
import pyodbc
from redis import StrictRedis
import pyodbc
from otp_api import configure_otp_api
from registration_api import configure_registration_api

app = Flask(__name__)
redis_client = StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

server = 'LAPTOP-CL5T1L6N\SQLEXPRESS'
database = 'epicore'
driver = 'SQL Server'

connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database}'
sql_conn = pyodbc.connect(connection_string)
cursor = sql_conn.cursor()

cursor.execute('''
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'users')
    BEGIN
        CREATE TABLE users (
            id INT IDENTITY(1,1) PRIMARY KEY,
            name NVARCHAR(50) NOT NULL,
            age INT NOT NULL,
            city NVARCHAR(50) NOT NULL,
            height FLOAT NOT NULL,
            weight FLOAT NOT NULL,
            mobile_number NVARCHAR(15) UNIQUE NOT NULL
        )
    END
''')
sql_conn.commit()

configure_otp_api(app, cursor, redis_client)
configure_registration_api(app, cursor, sql_conn)

if __name__ == '__main__':
    app.run(debug=True)
