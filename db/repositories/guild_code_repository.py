import datetime

from migration_engine import con


class AuthorizationCode:
    def __init__(self, code: str, created_at: datetime.datetime):
        self.code = code
        self.created_at = created_at
        self.expires_at = created_at + datetime.timedelta(days=2)


def insert_guild_code(code: str, creator_id: int) -> AuthorizationCode:
    created_at = datetime.datetime.now().astimezone(datetime.timezone.utc)
    con.execute("INSERT INTO GuildVerifications (Code, CreatedBy, CreatedAt) VALUES (?, ?, ?)",
                (code, creator_id, created_at))
    con.commit()
    return AuthorizationCode(code, created_at)


def is_valid_guild_code(code: str) -> bool:
    timestamp = con.execute("SELECT CreatedAt FROM GuildVerifications WHERE Code = ?", (code,)).fetchone()
    if timestamp is not None:
        created_at = datetime.datetime.strptime(timestamp[0], "%Y-%m-%d %H:%M:%S.%f%z")
        return created_at + datetime.timedelta(days=2) > datetime.datetime.now().astimezone(datetime.timezone.utc)
    return False


def insert_user_code(code: str, creator_id: int) -> AuthorizationCode:
    created_at = datetime.datetime.now().astimezone(datetime.timezone.utc)
    con.execute("INSERT INTO EmailVerifications (Code, UserID, CreatedAt) VALUES (?, ?, ?)",
                (code, creator_id, created_at))
    con.commit()
    return  AuthorizationCode(code, created_at)


def is_valid_user_code(code: str, user_id: int) -> bool:
    timestamp = con.execute("SELECT CreatedAt FROM EmailVerifications WHERE Code = ? AND UserID = ?", (code, user_id))\
        .fetchone()
    if timestamp is not None:
        created_at = datetime.datetime.strptime(timestamp[0], "%Y-%m-%d %H:%M:%S.%f%z")
        return created_at + datetime.timedelta(days=2) > datetime.datetime.now().astimezone(datetime.timezone.utc)
    return False
