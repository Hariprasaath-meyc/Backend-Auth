import json
import os
from dotenv import load_dotenv
from urllib.parse import urlencode

import urllib

load_dotenv()


GITHUB_CLIENT_ID = os.getenv(
    "GITHUB_CLIENT_ID"
)

GITHUB_CLIENT_SECRET = os.getenv(
    "GITHUB_CLIENT_SECRET"
)

GITHUB_REDIRECT_URI = os.getenv(
    "GITHUB_REDIRECT_URI"
)



def get_github_authorization_url(state):

    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "state": state,
        "scope": "user:email"
    }

    github_url= (
        "https://github.com/login/oauth/authorize?"
        + urlencode(params)
    )

    return github_url

def exchange_code_for_token(code):

    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": GITHUB_REDIRECT_URI
    }

    encoded_data = urllib.parse.urlencode(data).encode("utf-8")

    request = urllib.request.Request(
        "https://github.com/login/oauth/access_token",
        data=encoded_data,
        method="POST"
    )

    request.add_header(
        "Accept",
        "application/json"
    )

    try:

        with urllib.request.urlopen(request) as response:

            response_body = response.read().decode("utf-8")

            return json.loads(response_body)

    except urllib.error.HTTPError as error:

        print(
            "GitHub token exchange failed:",
            error.code
        )

        return None
#Retrieve the user with the access token
def get_github_user(access_token):

    request = urllib.request.Request(
        "https://api.github.com/user",
        method="GET"
    )

    request.add_header(
        "Authorization",
        f"Bearer {access_token}"
    )

    request.add_header(
        "Accept",
        "application/vnd.github+json"
    )

    request.add_header(
        "X-GitHub-Api-Version",
        "2022-11-28"
    )

    try:

        with urllib.request.urlopen(request) as response:

            response_body = response.read().decode("utf-8")

            return json.loads(response_body)

    except urllib.error.HTTPError as error:

        print(
            "GitHub user request failed:",
            error.code
        )

        return None

    
def get_github_emails(access_token):

    request = urllib.request.Request(
        "https://api.github.com/user/emails",
        method="GET"
    )

    request.add_header(
        "Authorization",
        f"Bearer {access_token}"
    )

    request.add_header(
        "Accept",
        "application/vnd.github+json"
    )

    request.add_header(
        "X-GitHub-Api-Version",
        "2026-03-10"
    )

    try:

        with urllib.request.urlopen(request) as response:

            response_body = response.read().decode(
                "utf-8"
            )

            print(
                "GitHub OAuth scopes:",
                response.headers.get("X-OAuth-Scopes")
            )

            return json.loads(response_body)

    except urllib.error.HTTPError as error:

        print(
            "GitHub email request failed:",
            error.code
        )

        print(
            "GitHub OAuth scopes:",
            error.headers.get("X-OAuth-Scopes")
        )

        error_body = error.read().decode(
            "utf-8"
        )

        print(
            "GitHub error:",
            error_body
        )

        return None

    request = urllib.request.Request(
        "https://api.github.com/user/emails",
        method="GET"
    )

    request.add_header(
        "Authorization",
        f"Bearer {access_token}"
    )

    request.add_header(
        "Accept",
        "application/vnd.github+json"
    )

    request.add_header(
        "X-GitHub-Api-Version",
        "2022-11-28"
    )

    try:
        with urllib.request.urlopen(request) as response:

            response_body = response.read().decode("utf-8")

            return json.loads(response_body)

    except urllib.error.HTTPError as error:

        print(
            "GitHub email request failed:",
            error.code
        )

        return None

print("Client ID:", GITHUB_CLIENT_ID)
print("Redirect URI:", GITHUB_REDIRECT_URI)