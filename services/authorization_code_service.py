import string
import random

from db.repositories import guild_code_repository, user_code_repository
from db.repositories.guild_code_repository import AuthorizationCode
from db.repositories.user_code_repository import UserAuthorizationCode


class InvalidCode(Exception):
    pass


def generate_guild_code(user_id: int) -> AuthorizationCode:
    code = generate_random_code()
    return guild_code_repository.insert(code, user_id)


def generate_user_code(user_id: int) -> UserAuthorizationCode:
    code = generate_random_code()
    return user_code_repository.insert(code, user_id)


def validate_codes(guild_code: str, user_code: str, user_id: int) -> bool:
    if not guild_code_repository.is_valid(guild_code):
        raise InvalidCode("Invalid guild code!")
    if not user_code_repository.is_valid(user_code, user_id):
        raise InvalidCode("Invalid user code!")


def generate_random_code(length: int = 6) -> str:
    possible_characters = string.ascii_letters + string.digits + string.punctuation
    code = ""
    random_generator = random.SystemRandom()
    for _ in range(length):
        code += random_generator.choice(possible_characters)
    return code
