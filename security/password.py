from argon2 import PasswordHasher

password_hasher = PasswordHasher()


def hash_password(password):
    return password_hasher.hash(password)


def verify_password(password, stored_hash):
    try:
        password_hasher.verify(stored_hash, password)
        return True
    except Exception:
        return False