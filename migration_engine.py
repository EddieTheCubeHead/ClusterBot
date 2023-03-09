import sqlite3
import os

_DB_FILE = "persistence/bot_db.sqlite"
_MIGRATION_FILE_FOLDER = "db/migrations"
_con = sqlite3.connect(_DB_FILE)


def on_deploy():
    latest_migrated = get_latest_migrated()
    latest_migrated = _run_migrations(latest_migrated)
    _set_last_migration(latest_migrated)
    pass


def get_latest_migrated() -> int:
    try:
        latest_migrated = _con.execute("SELECT LastFile FROM Migrations ORDER BY CreatedAt DESC").fetchone()[0]
    except sqlite3.Error:
        latest_migrated = 0
    return latest_migrated


def _run_migrations(latest_migrated: int) -> int:
    max_migrated = latest_migrated
    for file in os.listdir(_MIGRATION_FILE_FOLDER):
        if _should_read(file, latest_migrated):
            with open(f"{_MIGRATION_FILE_FOLDER}/{file}", "r", encoding="utf-8") as script:
                _con.executescript(script.read())
                _con.commit()
            max_migrated = max(int(file.split("_")[0]), max_migrated)
    return max_migrated


def _should_read(file_name: str, latest_migrated: int) -> bool:
    return file_name.endswith(".sql") and int(file_name.split("_")[0]) > latest_migrated


def _set_last_migration(file_number: int):
    _con.execute("INSERT INTO Migrations (LastFile) VALUES (?)", (file_number,))
    _con.commit()
