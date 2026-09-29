class RegisterUserDTO:

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

class LoginUserDTO:

        def __init__(self, email, password):
                self.email = email
                self.password = password
class ForgotPasswordDTO:

    def __init__(self, email):
        self.email = email
class ChangePasswordDTO:
     
     def __init__(self,email,new_password):
          self.email=email
          self.new_password=new_password