import datetime

from migration_engine import con


class UserAuthorizationCode:
    def __init__(self, code: str, created_at: datetime.datetime):
        self.code = code
        self.created_at = created_at
        self.expires_at = created_at + datetime.timedelta(days=2)


def insert(code: str, creator_id: int) -> UserAuthorizationCode:
    created_at_raw = con.execute("INSERT INTO EmailVerifications (Code, UserID) VALUES (?, ?) RETURNING CreatedAt",
                                 (code, creator_id)).fetchone()[0]
    created_at = datetime.datetime.strptime(created_at_raw, "%Y-%m-%d %H:%M:%S")
    con.commit()
    return UserAuthorizationCode(code, created_at)


def is_valid(code: str, user_id: int) -> bool:
    timestamp = con.execute("SELECT CreatedAt FROM EmailVerifications WHERE Code = ? AND UserID = ?", (code, user_id))\
        .fetchone()
    if timestamp is not None:
        created_at = datetime.datetime.strptime(timestamp[0], "%Y-%m-%d %H:%M:%S")
        return created_at + datetime.timedelta(days=2) > datetime.datetime.now()
    return False
