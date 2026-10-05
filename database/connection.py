import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

db_password = os.getenv("DB_PASSWORD")
db_host=os.getenv("DB_HOST")
db_port=os.getenv("DB_PORT")
db_name=os.getenv("DB_NAME")
db_user=os.getenv("DB_USER")





def get_connection():

    return psycopg.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password
    )