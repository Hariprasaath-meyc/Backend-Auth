

import psycopg


def get_connection():
    connection = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="auth-sample",
        user="postgres",
        password="hari@1355"
    )

    return connection