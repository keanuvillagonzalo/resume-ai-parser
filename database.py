import sqlite3
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY=os.getenv("API_KEY")
DATABASE_URL=os.getenv("DATABASE_URL")



def test_db_connection():

    try:

        conn = sqlite3.connect(DATABASE_URL)

        cursor = conn.cursor()


        cursor.execute("SELECT 1;")

        result = cursor.fetchone()


        print('\n'," sqlite Database Connection OK:", result, '\n')


        conn.close()



    except sqlite3.Error as e:

        print("Connection failed:", e) 