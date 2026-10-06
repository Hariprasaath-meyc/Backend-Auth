from database.connection import get_connection
from model.user_model import User

def find_user_by_email(email):

    connection=get_connection()

    cursor=connection.cursor()

    cursor.execute(
        """ 
        SELECT id,name,email,password_hash,auth_provider,provider_user_id
        FROM users
        WHERE email =%s
        """,
        (email,)  ##Getting the email as a tuple 
    )

    user=cursor.fetchone()

    cursor.close()
    connection.close()


    if user is None:
        return None

    return User(
        id=user[0],
        name=user[1],
        email=user[2],
        password_hash=user[3],
        auth_provider=user[4],
        provider_user_id=user[5]
    )

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

def create_new_user(
    name,
    email,
    password_hash,
    auth_provider,
    provider_user_id
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO users (
            name,
            email,
            password_hash,
            auth_provider,
            provider_user_id
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING
            id,
            name,
            email,
            password_hash,
            auth_provider,
            provider_user_id
        """,
        (
            name,
            email,
            password_hash,
            auth_provider,
            provider_user_id
        )
    )

    user = cursor.fetchone()

    connection.commit()

    cursor.close()
    connection.close()

    if user is None:
        return None

    return User(
        id=user[0],
        name=user[1],
        email=user[2],
        password_hash=user[3],
        auth_provider=user[4],
        provider_user_id=user[5]
    )

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

def find_user_by_id(id):

    connection=get_connection()

    cursor=connection.cursor()

    cursor.execute(
        """ 
        SELECT id,name,email,password_hash
        FROM users
        WHERE id =%s
        """,
        (id,)  ##Getting the email as a tuple 
    )

    user=cursor.fetchone()

    cursor.close()
    connection.close()

    return user
#Updating user New Passowrd with email jwt identifcation
def update_password_by_id(user_id, password_hash):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE users
        SET password_hash = %s
        WHERE id = %s
        """,
        (password_hash, user_id)
    )

    print("Rows updated:", cursor.rowcount)

    connection.commit()

    cursor.close()
    connection.close()
    


