import sqlite3
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY=os.getenv("API_KEY")
DATABASE_URL=os.getenv("DATABASE_URL")


def init_db():

    conn = sqlite3.connect(DATABASE_URL)

    c = conn.cursor()

    # Create table to store the raw JSON experiences per resume

    c.execute('''CREATE TABLE IF NOT EXISTS parsed_resumes 

                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 

                  filename TEXT, 

                  experience_json TEXT)''')

    conn.commit()

    conn.close()


def save_experiences(filename, data_list):

    conn = sqlite3.connect(DATABASE_URL)

    c = conn.cursor()

    c.execute("INSERT INTO parsed_resumes (filename, experience_json) VALUES (?, ?)", 

              (filename, json.dumps(data_list)))

    conn.commit()

    conn.close()


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