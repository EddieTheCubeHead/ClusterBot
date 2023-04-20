import json
import os


def get_secret(secret_name: str) -> str | int:
    return _get_env_or_from_file(secret_name, "dev_secrets.json")


def get_config(config_name: str) -> str | int:
    return _get_env_or_from_file(config_name, "config.json")


def _get_env_or_from_file(setting_name: str, file_name: str) -> str | int:
    setting = os.getenv(setting_name, None)
    if setting is None:
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        with open(file_path, "r", encoding="utf-8") as setting_file:
            setting = json.loads(setting_file.read())[setting_name]
    return setting
