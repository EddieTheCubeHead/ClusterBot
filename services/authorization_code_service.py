import string
import random

from db.repositories.guild_code_repository import AuthorizationCode, insert_guild_code, insert_user_code, \
    is_valid_guild_code, is_valid_user_code


class InvalidCode(Exception):
    pass


def generate_guild_code(user_id: int) -> AuthorizationCode:
    code = generate_random_code()
    return insert_guild_code(code, user_id)


def generate_user_code(user_id: int) -> AuthorizationCode:
    code = generate_random_code()
    return insert_user_code(code, user_id)


def validate_codes(guild_code: str, user_code: str, user_id: int) -> bool:
    if not is_valid_guild_code(guild_code):
        raise InvalidCode("Invalid guild code!")
    if not is_valid_user_code(user_code, user_id):
        raise InvalidCode("Invalid user code!")


def generate_random_code(length: int = 6) -> str:
    possible_characters = string.ascii_letters + string.digits + string.punctuation
    code = ""
    random_generator = random.SystemRandom()
    for _ in range(length):
        code += random_generator.choice(possible_characters)
    return code
