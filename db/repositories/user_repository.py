import datetime

from migration_engine import con


def ensure_exists(user_id: int):
    if con.execute("SELECT EXISTS(SELECT 1 FROM Users WHERE ID = ?)", (user_id,)).fetchone()[0] == 0:
        con.execute("INSERT INTO Users (ID) VALUES (?)", (user_id,))


def is_verified(user_id: int, max_timedelta: datetime.timedelta = datetime.timedelta(days=365)):
    ensure_exists(user_id)
    timestamp_raw = con.execute("SELECT VerifiedAt FROM Users WHERE ID = ?", (user_id,)).fetchone()[0]
    if timestamp_raw is None:
        return False
    verified_at = datetime.datetime.strptime(timestamp_raw, "%Y-%m-%d %H:%M:%S")
    return verified_at + max_timedelta > datetime.datetime.now()


def add_registered(user_id: int):
    con.execute("UPDATE Users SET (VerifiedAt) = CURRENT_TIMESTAMP WHERE ID = ?", (user_id,))
    con.commit()
