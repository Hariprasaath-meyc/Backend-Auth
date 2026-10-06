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
        password_hash,
        "local",
        None
    )

    return user

#GitHub Login
def github_login(github_user,github_email):

    existing_user = find_user_by_email(
        github_email
    )

    if existing_user:

        print("GitHub user already exists")

        return existing_user
    
    print("GitHub user does not exist. Creating user.")
    
    user = create_new_user(
        github_user["name"] or github_user["login"],
       github_email,
        None,
        "github",
        str(github_user["id"])
    )

    return user