class User:
    def __init__(
        self,
        id,
        name,
        email,
        password_hash,
        auth_provider,
        provider_user_id
    ):
        self.id=id
        self.name=name
        self.email=email
        self.password_hash=password_hash
        self.auth_provider=auth_provider
        self.provider_user_id=provider_user_id