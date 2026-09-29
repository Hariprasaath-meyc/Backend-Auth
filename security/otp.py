import secrets
def generate_otp():
    otp = secrets.randbelow(900000) + 100000
    print("Generated OTP:",otp)
    return otp