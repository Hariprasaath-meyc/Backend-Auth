from repositories.user_repositories import (
    create_new_user,
    find_user_by_email
)

from security.password import hash_password


def register_user(register_data):

    existing_user = find_user_by_email(
        register_data.email
    )

    if existing_user:
        return "User already exists"

    password_hash = hash_password(
        register_data.password
    )

    user = create_new_user(
        register_data.name,
        register_data.email,
        password_hash
    )

    return user