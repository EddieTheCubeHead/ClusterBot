import secrets
import hashlib
from dataclasses import dataclass


@dataclass
class HashedVote:
    hash: str
    salt: str


def create_hash(option_name: str) -> HashedVote:
    salt = secrets.token_hex(16)
    hashed_vote = create_from_salt(option_name, salt)
    return HashedVote(hashed_vote, salt)


def create_from_salt(option_name: str, salt: str) -> str:
    return hashlib.sha256(bytes(f"{option_name};{salt}", "UTF-8")).hexdigest()
