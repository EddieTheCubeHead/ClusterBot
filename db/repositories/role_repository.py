from migration_engine import con


def get_uninitialized_roles() -> list[(str, int)]:
    return con.execute("SELECT Name, Colour FROM Roles WHERE ID IS NULL ").fetchall()


def mark_as_initialized(role: str, role_id: int):
    con.execute("UPDATE Roles SET ID = ? WHERE Name = ?", (role_id, role))
    con.commit()


def get_role_id(name: str) -> int:
    return con.execute("SELECT ID FROM Roles WHERE Name = ?", (name,)).fetchone()[0]
