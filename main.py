from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from validators.json_validator import send_json_response
from services.auth_service import register_user
from dto.auth_dto import (
    RegisterUserDTO,
    LoginUserDTO,
    ForgotPasswordDTO,
    ChangePasswordDTO
)   
from repositories.user_repositories import (
    find_user_by_email,
    find_all_users,
    update_password,
    find_user_by_id
    )
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
        
    #JSON Response
    def send_json_response(self, status_code, response):

        response_body = json.dumps(
            response
        ).encode("utf-8")

        self.send_response(status_code)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Content-Length",
            str(len(response_body))
        )

        self.end_headers()
        try:
            self.wfile.write(response_body)
            self.wfile.flush()

        except ConnectionAbortedError:
            print("Client closed the connection before receiving the response.")
            

    

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

            self.send_json_response(
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

                self.send_json_response(
                    400,
                    {"message":f"{field} is required"}
                )
                return

        #Email Validation
        if not data["email"].endswith("@gmail.com"):

            self.send_json_response(
                400,
                {"message":"Enter a Valid Gmail Address"}
            )

        #Password Validation
        if len(data["password"]) < 8:

            self.send_json_response(
                400,
                {"message":"Password must be atleast 8 characters"}
            )
            return

        
        result = register_user(register_data)

        #Existing User Validation
        if result == "User already exists":

           self.send_json_response(
               409,
               {"message":"User Already Exists"}

           )
           return

        else:

            self.send_json_response(
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

            self.send_json_response(
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

                self.send_json_response(
                    400,
                    {"message": f"{field} is required"}
                )

                return

        # Email Validation
        if not data["email"].endswith("@gmail.com"):

            self.send_json_response(
                400,
                {"message": "Enter a Valid Gmail Address"}
            )

            return

        # Password Validation
        if len(data["password"]) < 8:

            self.send_json_response(
                400,
                {"message": "Password must be at least 8 characters"}
            )

            return
        
        user = find_user_by_email(
        login_data.email
        )
        if not user:

         self.send_json_response
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

            self.send_json_response(
                401,
                {"message": "Invalid email or password"}
            )

            return
        
        token =generate_token(
            user[0],
            user[1]
        )
        self.send_json_response(
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

            self.send_json_response(
                400,
                {"message": "Invalid Json Response"}
            )

            return
        
        required_fields = ["email"]

        for field in required_fields:

            if field not in data or not data[field]:

                self.send_json_response(
                    400,
                    {"message": f"{field} is required"}
                )

                return
        if not data["email"].endswith("@gmail.com"):

            self.send_json_response(
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

            self.send_json_response(
                404,
                {"message": "User not found"}
            )

            return
        otp = generate_otp()

        otp_storage[forgot_password_data.email] = otp

        
        print("OTP Storage:", otp_storage)

        self.send_json_response(
       200,
        {"message": "OTP generated successfully"}
        )

    
    def handle_change_password(self):

            
        print("Change password Endpoint working")
        self.send_json_response(
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

            self.send_json_response(
                400,
                {"message": "Invalid Json Response"}
            )

            return
        #Field Validation
        required_fields = ["email", "new_password"]

        for field in required_fields:
            
            if field not in data or not data[field]:

                self.send_json_response(
                    400,
                    {"message": f"{field} is required"}
                )

                return
        #Email Validation
        if not data["email"].endswith("@gmail.com"):

            self.send_json_response(
                400,
                {"message": "Enter a Valid Gmail Address"}
            )

            return
        #New password Verification
        if len(data["new_password"]) < 8:

            self.send_json_response(
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

            self.send_json_response(
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

        self.send_json_response(
        200,
        {"message": "Password changed successfully"}
        )




    #Retrive All users   
    def handle_users(self):

        users = find_all_users()

        self.send_json_response(
            200,
            {
                "users": users
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

            self.send_json_response(
                400,
                {"message": "Invalid Json Response"}
            )

            return
        required_fields = ["email", "otp"]

        for field in required_fields:

            if field not in data or not data[field]:

                self.send_json_response(
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

            self.send_json_response(
                400,
                {"message": "Invalid OTP"}
            )

            return
       
        
        #Successful OTP Verification
        verified_users[data["email"]] = True
        
        print("Verified users:", verified_users)
        
        self.send_json_response(
            200,
        {"message": "OTP verified successfully"}
        )
    
    #Reser Password  
    def handle_reset_password(self):

        print("Reset password endpoint called")

        authorization = self.headers.get("Authorization")

        print("Authorization header:", authorization)

        if not authorization:

            self.send_json_response(
                401,
                {"message": "Authorization header required"}
            )

            return

        parts = authorization.split(" ")

        if len(parts) != 2 or parts[0] != "Bearer":

            self.send_json_response(
                401,
                {"message": "Invalid authorization header"}
            )

            return

        token = parts[1]

        payload=verify_token(token)
        print("JWT payload:", payload)

        if payload is None:
            self.send_json_response(
                401,
                {"message":"Invalid token"}
            )
            return
        
        user_id=payload["user_id"]

        print("Authenticated User ID:",user_id)

        user = find_user_by_id(user_id)

        if not user:

            self.send_json_response(
                404,
                {"message": "User not found"}
            )

            return
            

    

        

server = HTTPServer(
    ("localhost", 8000),
    AuthHandler
)
users = find_all_users()
print("Server running on http://localhost:8000")

server.serve_forever()