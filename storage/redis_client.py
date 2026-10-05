import redis


redis_client = redis.Redis(
    host="localhost",
    port=6379,
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

if __name__ == "__main__":

    store_otp(
        "hari@gmail.com",
        489321
    )
    otp=get_otp(
        "hari@gmail.com"
    )
    print("Redis OTP:",otp)

    delete_otp(
        "hari@gmail.com"
    )

    otp=get_otp(
        "hari@gmail.com"
    )

    print("Redis OTP after deletion:",otp)
    