import redis
import os
from dotenv import load_dotenv

load_dotenv()

redis_host=os.getenv("REDIS_HOST")
redis_port = int(os.getenv("REDIS_PORT", 6379))


redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    decode_responses=True
)

def store_otp(email, otp):

    redis_client.set(
        f"otp:{email}",
        str(otp),
        ex=300
    )


def get_otp(email):

    return redis_client.get(
        f"otp:{email}"
    )


def delete_otp(email):

    redis_client.delete(
        f"otp:{email}"
    )
#OAuth State Storage
def store_oauth_state(state):
    redis_client.set(
        f"oauth_state:{state}",
        "1",
        ex=300
    )


def get_oauth_state(state):
    return redis_client.get(
        f"oauth_state:{state}"
    )


def delete_oauth_state(state):
    redis_client.delete(
        f"oauth_state:{state}"
    )


    