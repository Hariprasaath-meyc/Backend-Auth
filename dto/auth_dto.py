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

class ResetPasswordDTO:

    def __init__(self, old_password, new_password):

        self.old_password = old_password
        self.new_password = new_password

class RetrieveUsersDTO:
    def __init__(self,id,name,email):
        self.id=id
        self.name=name 
        self.email=email