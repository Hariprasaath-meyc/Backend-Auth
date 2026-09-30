import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

db_password = os.getenv("DB_PASSWORD")




def get_connection():

    return psycopg.connect(
        host="localhost",
        port=5432,
        dbname="authdb",
        user="postgres",
        password=db_password
    )