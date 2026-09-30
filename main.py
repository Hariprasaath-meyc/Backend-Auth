from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from validators.json_validator import send_json_response
from services.auth_service import register_user
from dto.auth_dto import (
    RegisterUserDTO,
    LoginUserDTO,
    ForgotPasswordDTO,
    ChangePasswordDTO,
    ResetPasswordDTO,
    RetrieveUsersDTO

)   
from repositories.user_repositories import (
    find_user_by_email,
    find_all_users,
    update_password,
    find_user_by_id,
    update_password_by_id
    )
from validators.json_validator import send_json_response
from security.password import verify_password,hash_password
from repositories.user_repositories import find_all_users
from security.otp import generate_otp
from security.jwt import generate_token, verify_token




# OTP storage
otp_storage = {}

verified_users = {}


class AuthHandler(BaseHTTPRequestHandler):
    #Endpoint For Data Creation/Adding
    def do_POST(self):

        if self.path == "/register":
            self.handle_register()
        
        elif self.path == "/login":
            self.handle_login()

        elif self.path == "/forgot-password":
            self.handle_forgot_password()

        elif self.path == "/change-password":
            self.handle_change_password()

        elif self.path == "/verify-otp":
            self.handle_verify_otp()

        elif self.path == "/reset-password":
            self.handle_reset_password()

       

        else:
            self.send_response(404)
            self.end_headers()

            self.wfile.write(
                b"Endpoint not found"
            )

    #Endpoint for Data Retireval
    def do_GET(self):

        if self.path=="/users":
            self.handle_users()
        

    #User Registration 
    def handle_register(self):

        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        body = self.rfile.read(content_length)

        print("Received body:")
        print(body)
        #JSON Data Validation
        try:
            data = json.loads(body)

        except json.JSONDecodeError:

            send_json_response(
                400,
                {"message":"Invalid Json Response"}
            )

            return
        #DTO Data Request
        register_data = RegisterUserDTO(
            data["name"],
            data["email"],
            data["password"]
        )
        #Input Data Validation
        required_fields = ["name", "email", "password"]

        for field in required_fields:

            if field not in data:

                send_json_response(
                    400,
                    {"message":f"{field} is required"}
                )
                return

        #Email Validation
        if not data["email"].endswith("@gmail.com"):

            send_json_response(
                400,
                {"message":"Enter a Valid Gmail Address"}
            )

        #Password Validation
        if len(data["password"]) < 8:

            send_json_response(
                400,
                {"message":"Password must be atleast 8 characters"}
            )
            return

        
        result = register_user(register_data)

        #Existing User Validation
        if result == "User already exists":

           send_json_response(
               409,
               {"message":"User Already Exists"}

           )
           return

        else:

            send_json_response(
                201,
                {"message":"User Registered Successfully!"}
            )

    #User SignIN
    def handle_login(self):

        print("Login endpoint called")

        # Read request body
        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        body = self.rfile.read(content_length)

        print("Received login body:")
        print(body)

        # Convert JSON into Python dictionary
        try:
            data = json.loads(body)

        except json.JSONDecodeError:

            send_json_response(
                400,
                {"message": "Invalid Json Response"}
            )

            return
        #Login DTO
        login_data = LoginUserDTO(
            data["email"],
            data["password"]
        )

        # Input Data Validation
        required_fields = ["email", "password"]

        for field in required_fields:

            if field not in data or not data[field]:

                send_json_response(
                    400,
                    {"message": f"{field} is required"}
                )

                return

        # Email Validation
        if not data["email"].endswith("@gmail.com"):

            send_json_response(
                400,
                {"message": "Enter a Valid Gmail Address"}
            )

            return

        # Password Validation
        if len(data["password"]) < 8:

            send_json_response(
                400,
                {"message": "Password must be at least 8 characters"}
            )

            return
        
        user = find_user_by_email(
        login_data.email
        )
        if not user:

         send_json_response
         ( 401,
        {"message": "Invalid email or password"}
            )
         return

        stored_password_hash = user[3]
    
        password_valid = verify_password(
               login_data.password,
                stored_password_hash
            )
        
        if not password_valid:

            send_json_response(
                401,
                {"message": "Invalid email or password"}
            )

            return
        
        token =generate_token(
            user[0],
            user[1]
        )
        send_json_response(
                200,
        {
            "message": "Login successful",
            "token":token
            }
        )
        
        
    #Forgot Password
    def handle_forgot_password(self):


        print("Forgot password endpoint called")

        # Read request body
        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        body = self.rfile.read(content_length)

        print("Received forgot password body:")
        print(body)

        # Convert JSON into Python dictionary
        try:
            data = json.loads(body)
            print("Parsed data:")
            print(data)

            print("Email:")
            print(data["email"])

        except json.JSONDecodeError:

            send_json_response(
                400,
                {"message": "Invalid Json Response"}
            )

            return
        
        required_fields = ["email"]

        for field in required_fields:

            if field not in data or not data[field]:

                send_json_response(
                    400,
                    {"message": f"{field} is required"}
                )

                return
        if not data["email"].endswith("@gmail.com"):

            send_json_response(
                400,
                {"message": "Enter a Valid Gmail Address"}
            )

            return
        
        #Forgot Password DTO
        forgot_password_data=ForgotPasswordDTO(
            data["email"]
        )

        user=find_user_by_email(
            forgot_password_data.email
        )

        if not user:

            send_json_response(
                404,
                {"message": "User not found"}
            )

            return
        otp = generate_otp()

        otp_storage[forgot_password_data.email] = otp

        
        print("OTP Storage:", otp_storage)

        send_json_response(
       200,
        {"message": "OTP generated successfully"}
        )

    #Reset Password
    def handle_change_password(self):

            
        print("Change password Endpoint working")
        send_json_response(
            200,
            {"message":"Change password enpoint working"}
        )
        content_length = int(
        self.headers.get("Content-Length", 0)
        )

        body = self.rfile.read(content_length)

        print("Received change password body:")

        print(body)

        try:

            data = json.loads(body)

        except json.JSONDecodeError:

            send_json_response(
                400,
                {"message": "Invalid Json Response"}
            )

            return
        #Field Validation
        required_fields = ["email", "new_password"]

        for field in required_fields:
            
            if field not in data or not data[field]:

                send_json_response(
                    400,
                    {"message": f"{field} is required"}
                )

                return
        #Email Validation
        if not data["email"].endswith("@gmail.com"):

            send_json_response(
                400,
                {"message": "Enter a Valid Gmail Address"}
            )

            return
        #New password Verification
        if len(data["new_password"]) < 8:

            send_json_response(
                400,
                {"message": "Password must be at least 8 characters"}
            )

            return
            
        #DTO Request
        change_password_data=ChangePasswordDTO(
            data["email"],
            data["new_password"]
        )

        verified = verified_users.get(
            change_password_data.email
        )

        #Verification of Users
        if not verified:

            send_json_response(
                401,
                {"message": "OTP verification required"}
            )

            return
        
        #Hash the New Password
        new_password_hash=hash_password(
            change_password_data.new_password
        )
        print("New password hash generated:", new_password_hash)
        #Update the password in Database
        update_password(
        change_password_data.email,
        new_password_hash
        )

        send_json_response(
        200,
        {"message": "Password changed successfully"}
        )


    #Retrive All users   
    def handle_users(self):

        users = find_all_users()
        response_users=[]

        for user in users:
            user_dto=RetrieveUsersDTO(
                user[0],
                user[1],
                user[2]
            )
            response_users.append(user_dto)
            
            response_data=[]
            for user in response_users:

                response_data.append(
                    {
                    "id":user.id,
                    "name":user.name,
                    "email":user.email
                    }
                )

        send_json_response(
            200,
            {
                "users": response_data
            }
        )

    def handle_verify_otp(self):
        
        print("Verify OTP endpoint called")

        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        body = self.rfile.read(content_length)

        print("Received verify OTP body:")
        print(body)
        try:

            data = json.loads(body)

        except json.JSONDecodeError:

            send_json_response(
                400,
                {"message": "Invalid Json Response"}
            )

            return
        required_fields = ["email", "otp"]

        for field in required_fields:

            if field not in data or not data[field]:

                send_json_response(
                    400,
                    {"message": f"{field} is required"}
                )

                return
       
        #Get the OTP
        stored_otp = otp_storage.get(
            data["email"]
        )
        
        

        #OTP Verification
        if stored_otp != data["otp"]:
            print(">>> Sending 400 Invalid OTP")

            send_json_response(
                400,
                {"message": "Invalid OTP"}
            )

            return
       
        
        #Successful OTP Verification
        verified_users[data["email"]] = True
        
        print("Verified users:", verified_users)
        
        send_json_response(
            200,
        {"message": "OTP verified successfully"}
        )
    
    #Reser Password  
    def handle_reset_password(self):

        print("Reset password endpoint called")

        authorization = self.headers.get("Authorization")

        print("Authorization header:", authorization)

        if not authorization:

            send_json_response(
                401,
                {"message": "Authorization header required"}
            )

            return

        parts = authorization.split(" ")

        if len(parts) != 2 or parts[0] != "Bearer":

            send_json_response(
                401,
                {"message": "Invalid authorization header"}
            )

            return

        token = parts[1]

        payload=verify_token(token)
        print("JWT payload:", payload)

        if payload is None:
            send_json_response(
                401,
                {"message":"Invalid token"}
            )
            return
        
        user_id=payload["user_id"]


        print("Authenticated User ID:",user_id)

        user = find_user_by_id(user_id)

        if not user:

            send_json_response(
                404,
                {"message": "User not found"}
            )

            return

        #Read the body
        print("Reading reset password body...")

        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        body = self.rfile.read(content_length)

        try:

            data = json.loads(body)

        except json.JSONDecodeError:

            send_json_response(
                400,
                {"message": "Invalid JSON"}
            )

            return
        #DTO Request Data
        reset_password_data = ResetPasswordDTO(
           reset_password_data.old_password,
            reset_password_data.new_password
        )
        
        required_fields = [
        "old_password",
        "new_password"  
            ]

        for field in required_fields:

            if field not in data or not data[field]:

                send_json_response(
                    400,
                    {"message": f"{field} is required"}
                )

                return
            
        stored_password_hash = user[3]

        print("Stored password hash:", stored_password_hash)

        
        if not verify_password(
            data["old_password"],
            stored_password_hash
        ):
            send_json_response(
            401,
            {"message": "Current password is incorrect"}
        )

            return
        
        print("Old password verified successfully")

        new_password_hash = hash_password(
            data["new_password"]
        )

        print("New password hashed successfully")

        update_password_by_id(
            user_id,
            new_password_hash
        )

        send_json_response(
            200,
            {
                "message":"Password resetted Successfully"
            }
        )

       
    

        

server = HTTPServer(
    ("localhost", 8000),
    AuthHandler
)

print("Server running on http://localhost:8000")

server.serve_forever()