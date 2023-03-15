import sqlite3
import os

_path_here = os.getcwd()
_DB_FILE = "persistence/bot_db.sqlite"
_MIGRATION_FILE_FOLDER = "db/migrations"
con = sqlite3.connect(f"{_path_here}/{_DB_FILE}")


def on_deploy():
    latest_migrated = get_latest_migrated()
    latest_migrated = _run_migrations(latest_migrated)
    _set_last_migration(latest_migrated)
    pass


def get_latest_migrated() -> int:
    try:
        latest_migrated = con.execute("SELECT LastFile FROM Migrations ORDER BY CreatedAt DESC").fetchone()[0]
    except sqlite3.Error:
        latest_migrated = 0
    return latest_migrated


def _run_migrations(latest_migrated: int) -> int:
    scripts = _get_scripts_to_run(latest_migrated)
    max_migrated = _run_scripts(latest_migrated, scripts)
    return max_migrated


def _run_scripts(max_migrated, scripts):
    for file_name in [script[1] for script in scripts]:
        print(f"Running migration script '{file_name}'")
        with open(f"{_MIGRATION_FILE_FOLDER}/{file_name}", "r", encoding="utf-8") as script:
            con.executescript(script.read())
            con.commit()
        max_migrated = max(int(file_name.split("_")[0]), max_migrated)
    return max_migrated


def _get_scripts_to_run(latest_migrated):
    scripts = []
    for file in os.listdir(_MIGRATION_FILE_FOLDER):
        if _should_read(file, latest_migrated):
            scripts.append((int(file.split("_")[0]), file))
    scripts.sort(key=lambda x: x[0])
    return scripts


def _should_read(file_name: str, latest_migrated: int) -> bool:
    return file_name.endswith(".sql") and int(file_name.split("_")[0]) > latest_migrated


def _set_last_migration(file_number: int):
    con.execute("INSERT INTO Migrations (LastFile) VALUES (?)", (file_number,))
    con.commit()
