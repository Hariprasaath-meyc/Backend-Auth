from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import secrets
from urllib.parse import urlparse, parse_qs
from security.jwt import generate_token
from storage.redis_client import store_oauth_state
from security.github_oauth import get_github_authorization_url
from services.auth_service import (
    register_user,
    github_login)

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
from schemas.auth_schema import (
    register_schema,
    login_schema,
    forgot_password_schema,
    reset_password_schema,
    change_password_schema,
    verify_otp_schema
)
from storage.redis_client import (
    get_oauth_state,
    delete_oauth_state
)

from storage.redis_client import store_otp,get_otp,delete_otp
from validators.json_validator import validate_request
from security.password import verify_password,hash_password
from repositories.user_repositories import find_all_users
from security.otp import generate_otp
from security.jwt import generate_token, verify_token
from security.github_oauth import (
    get_github_authorization_url,
    exchange_code_for_token,
     get_github_user,
     get_github_emails
)





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
            
        except (ConnectionAbortedError,BrokenPipeError):
            print("Client closed the connection before receiving the response.")
    #Endpoint for Data Retireval
    def do_GET(self):
         parsed_url = urlparse(self.path)

         path = parsed_url.path

         if path == "/users":
            self.handle_users()

         elif path == "/auth/github":
             self.handle_github_login()

         elif path == "/auth/github/callback":
             self.handle_github_callback()

         else:
            self.send_json_response(
            404,
            {"message": "Endpoint not found"}
        )
        
    

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
        
        #JSON Schema Validation
        is_valid, error = validate_request(
            data,
            register_schema
        )

        if not is_valid:
            self.send_json_response(
                400,
                {"message": error}
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

          
        #JSON Schema Validation for Login Data
        is_valid,error=validate_request(
           data,
           login_schema
       )

        if not is_valid:

            self.send_json_response(
                400,
                {"message": error}
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

        stored_password_hash = user.password_hash
    
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
            user.id,
            user.email
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
        
        # JSON Schema validation
        is_valid, error = validate_request(
            data,
            forgot_password_schema
        )

        if not is_valid:

            self.send_json_response(
                400,
                {"message": error}
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
        #Generate OTP
        otp = generate_otp()

        #Store OTP in Redis
        store_otp(
            forgot_password_data.email,
            otp
        )
        print(
        "OTP stored in Redis for:",
        forgot_password_data.email,
        flush=True
        )

        self.send_json_response(
         200,
        {"message": "OTP generated successfully"}
        )

    #Change Password
    def handle_change_password(self):

            
        print("Change password Endpoint working")
        self.send_json_response(
            200,
            {"message":"Change password endpoint working"}
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
        
        #JSON Schema Validation
        is_valid,error=validate_request(
            data,
            change_password_schema
        )

        if not is_valid:
            self.send_json_response(
                400,
                {"message": error}
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
        response_users = []

        for user in users:
            user_dto = RetrieveUsersDTO(
                user[0],
                user[1],
                user[2]
            )

            response_users.append(user_dto)

        response_data = []

        for user in response_users:
            response_data.append(
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                }
            )

        self.send_json_response(
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

            self.send_json_response(
                400,
                {"message": "Invalid Json Response"}
            )

            return
        
        is_valid,error=validate_request(
            data,
            verify_otp_schema
        )

        #JSON Schema Validation
        if not is_valid:
            self.send_json_response(
                400,
                {"message":"error"}
            )
       
        #Get the OTP
        stored_otp = get_otp(
            data["email"]
        )
        
        print("Stored OTP:",stored_otp)

        # OTP not found
        if stored_otp is None:

            self.send_json_response(
                400,
                {"message": "OTP expired or not found"}
            )

            return
        #OTP Verification
        if stored_otp != data["otp"]:
            print(">>> Sending 400 Invalid OTP")

            self.send_json_response(
                400,
                {"message": "Invalid OTP"}
            )

            return

        # OTP is correct
        print(">>> OTP verified successfully")

        # Delete OTP after successful verification
        delete_otp(
            data["email"]
        )
       
        
        #Successful OTP Verification
        verified_users[data["email"]] = True
        
        print("Verified users:", verified_users)
        
        self.send_json_response(
            200,
        {"message": "OTP verified successfully"}
        )
    
    #Reset Password  
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

        #Read the body
        print("Reading reset password body...")

        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        body = self.rfile.read(content_length)

        try:

            data = json.loads(body)

        except json.JSONDecodeError:

            self.send_json_response(
                400,
                {"message": "Invalid JSON"}
            )

            return
        #DTO Request Data
        reset_password_data = ResetPasswordDTO(
           reset_password_data.old_password,
            reset_password_data.new_password
        )

        #JSON Schema Validation
        is_valid,error=validate_request(
            data,
            reset_password_schema
        )
            
        stored_password_hash = user[3]

        if not is_valid:
            self.send_json_response(
                400,
                {"message": error}
            )
            return


        print("Stored password hash:", stored_password_hash)

        
        if not verify_password(
            data["old_password"],
            stored_password_hash
        ):
            self.send_json_response(
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

        self.send_json_response(
            200,
            {
                "message":"Password resetted Successfully"
            }
        )
   
    #Handling GitHub Login
    def handle_github_login(self):

        print("GitHub OAuth Started Successfully")

        state = secrets.token_urlsafe(32)

        print("Generated state:", state)

        store_oauth_state(state)

        print("OAuth state stored in Redis")

        github_url = get_github_authorization_url(state)

        print("GitHub URL:")
        print(github_url)

        self.send_response(302)

        self.send_header(
            "Location",
            github_url
        )

        self.end_headers()
    #CallBack function
    def handle_github_callback(self):

        print("GitHub OAuth callback received")

        parsed_url = urlparse(self.path)

        query_params = parse_qs(
            parsed_url.query
        )

        code = query_params.get(
            "code",
            [None]
        )[0]

        state = query_params.get(
            "state",
            [None]
        )[0]

        print("Authorization code:", code)
        print("State:", state)

        if not code:
            self.send_json_response(
                400,
                {"message": "Authorization code missing"}
            )
            return

        if not state:
            self.send_json_response(
                400,
                {"message": "State missing"}
            )
            return

        # Verify OAuth State

        stored_state = get_oauth_state(state)

        print("Stored state:", stored_state)

        if stored_state is None:

            self.send_json_response(
                400,
                {"message": "Invalid or expired OAuth state"}
            )
            return

        delete_oauth_state(state)

        print("OAuth state verified successfully")

        # Auth Token Exchange for Access Token

        token_response = exchange_code_for_token(code)

        print("GitHub token exchange completed")

        if token_response is None:

            self.send_json_response(
                500,
                {"message": "Failed to exchange authorization code"}
            )
            return

        # Safe debugging - do NOT print the access token

        print(
            "Token type:",
            token_response.get("token_type")
        )

        print(
            "Scope:",
            token_response.get("scope")
        )

        # Get GitHub Access Token

        access_token = token_response.get(
            "access_token"
        )

        if not access_token:

            self.send_json_response(
                500,
                {"message": "GitHub access token missing"}
            )
            return

        # Get GitHub User Details

        github_user = get_github_user(
            access_token
        )

        if github_user is None:

            self.send_json_response(
                500,
                {"message": "Failed to retrieve GitHub user"}
            )
            return

        # Get GitHub Email Addresses

        github_emails = get_github_emails(
            access_token
        )

        print(
            "GitHub emails:",
            github_emails
        )
        

        if github_emails is None:

            self.send_json_response(
                500,
                {"message": "Failed to retrieve GitHub email"}
            )
            return

        github_email = None

        for email_data in github_emails:

            if (
                email_data.get("primary")
                and email_data.get("verified")
            ):
                github_email = email_data.get("email")

                break
            
        if github_email is None:

            self.send_json_response(
                400,
                {
                    "message":
                    "No verified primary GitHub email found"
                }
            )
            return


        print(
            "GitHub email:",
            github_email
        )

        print(
            "GitHub user retrieved successfully"
        )

# Find or create application user

        user = github_login(
            github_user,
            github_email
        )

        print(
                "Application user ID:",
                user.id
            )

        print(
                "Application user email:",
                user.email
            )

        print(
                "Authentication provider:",
                user.auth_provider
            )

            # Generate application JWT

        token = generate_token(
                user.id,
                user.email
            )

        self.send_json_response(
                200,
                {
                    "message": "GitHub login successful",
                    "token": token
                }
            )
                




server = HTTPServer(
    ("0.0.0.0", 8000),
    AuthHandler
)

print("Server running on http://localhost:8000")

server.serve_forever()