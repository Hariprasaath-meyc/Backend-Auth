from database.connection import get_connection


def find_user_by_email(email):

    connection=get_connection()

    cursor=connection.cursor()

    cursor.execute(
        """ 
        SELECT id,name,email,password_hash
        FROM users
        WHERE email =%s
        """,
        (email,)  ##Getting the email as a tuple 
    )

    user=cursor.fetchone()

    cursor.close()
    connection.close()

    return user
def find_all_users():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, email, password_hash
        FROM users
        """
    )

    users = cursor.fetchall()

    cursor.close()
    connection.close()

    return users

def create_new_user(name,email,password_hash):

    connection=get_connection()

    cursor=connection.cursor()
    
    cursor.execute(
        """
        INSERT INTO users (name,email,password_hash)
        VALUES(%s,%s,%s)
        RETURNING id,name,email,password_hash
        """,
        (name,email,password_hash)
    )

    user=cursor.fetchone()

    connection.commit()

    cursor.close()

    connection.close()

    return user

def update_password(email,password_hash):
    print("Updating password for:", email)
    
    connection=get_connection()

    cursor=connection.cursor()

    cursor.execute(
        """
        UPDATE users 
        set password_hash=%s 
        WHERE email= %s
        """,
        (password_hash,email)
    )
    print("Rows updated:", cursor.rowcount)
    connection.commit()

    cursor.close()

    connection.close()

    
    

