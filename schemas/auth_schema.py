login_schema = {
    "type": "object",

    "properties": {
        "email": {
            "type": "string",
            "format": "email"
        },

        "password": {
            "type": "string",
            "minLength": 8
        }
    },

    "required": [
        "email",
        "password"
    ],

    "additionalProperties": False
}

register_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1
        },
        "email": {
            "type": "string",
            "format": "email"
        },
        "password": {
            "type": "string",
            "minLength": 8
        }
    },
    "required": [
        "name",
        "email",
        "password"
    ],
    "additionalProperties": False
}

forgot_password_schema = {
    "type": "object",

    "properties": {
        "email": {
            "type": "string",
            "format": "email"
        }
    },

    "required": [
        "email"
    ],

    "additionalProperties": False
}


reset_password_schema = {
    "type": "object",

    "properties": {
        "old_password": {
            "type": "string",
            "minLength": 8
        },

        "new_password": {
            "type": "string",
            "minLength": 8
        }
    },

    "required": [
        "old_password",
        "new_password"
    ],

    "additionalProperties": False
}

change_password_schema = {
    "type": "object",

    "properties": {
        "email": {
            "type": "string",
            "pattern": "^[A-Za-z0-9._%+-]+@gmail\\.com$"
        },

        "new_password": {
            "type": "string",
            "minLength": 8
        }
    },

    "required": [
        "email",
        "new_password"
    ],

    "additionalProperties": False
}

verify_otp_schema = {
    "type": "object",

    "properties": {
        "email": {
            "type": "string",
            "pattern": "^[A-Za-z0-9._%+-]+@gmail\\.com$"
        },

        "otp": {
            "type": "string",
            "pattern": "^[0-9]{6}$"
        }
    },

    "required": [
        "email",
        "otp"
    ],

    "additionalProperties": False
}
