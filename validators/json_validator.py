from jsonschema import validate
from jsonschema.exceptions import ValidationError


def validate_request(data, schema):

    try:
        validate(
            instance=data,
            schema=schema
        )

        return True, None

    except ValidationError as error:

        return False, error.message