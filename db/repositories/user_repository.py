import datetime
from dataclasses import dataclass

from migration_engine import con


@dataclass
class User:
    id: int
    verified_at: datetime.datetime
    email: str


def ensure_exists(user_id: int):
    created_at = datetime.datetime.now().astimezone(datetime.timezone.utc)
    if con.execute("SELECT EXISTS(SELECT 1 FROM Users WHERE ID = ?)", (user_id,)).fetchone()[0] == 0:
        con.execute("INSERT INTO Users (ID, CreatedAt) VALUES (?, ?)", (user_id, created_at))


def is_verified(user_id: int, max_timedelta: datetime.timedelta = datetime.timedelta(days=365)):
    ensure_exists(user_id)
    timestamp_raw = con.execute("SELECT VerifiedAt FROM Users WHERE ID = ?", (user_id,)).fetchone()[0]
    if timestamp_raw is None:
        return False
    verified_at = datetime.datetime.strptime(timestamp_raw, "%Y-%m-%d %H:%M:%S.%f%z")
    return verified_at + max_timedelta > datetime.datetime.now().astimezone(datetime.timezone.utc)


def get_user(user_id: int) -> User:
    user_data = con.execute("SELECT VerifiedAt, Email FROM Users WHERE ID = ?", (user_id,)).fetchone()
    return User(user_id, *user_data)


def add_registered(user_id: int, email: str):
    verified_at = datetime.datetime.now().astimezone(datetime.timezone.utc)
    con.execute("UPDATE Users SET (VerifiedAt, Email) = (?, ?) WHERE ID = ?", (verified_at, email, user_id))
    con.commit()
