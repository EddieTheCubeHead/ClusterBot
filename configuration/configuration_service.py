import json
import os


class _DefaultSentinel:
    pass


_default_sentinel = _DefaultSentinel()


def get_secret(secret_name: str, default: str | int | None = _default_sentinel) -> str | int | None:
    return _get_env_or_from_file(secret_name, "dev_secrets.json", default)


def get_config(config_name: str, default: str | int | None = _default_sentinel) -> str | int | None:
    return _get_env_or_from_file(config_name, "config.json", default)


def _get_env_or_from_file(setting_name: str, file_name: str, default: str | int | None = _default_sentinel) \
        -> str | int | None:
    setting = os.getenv(setting_name, None)
    if setting is None:
        try:
            file_path = os.path.join(os.path.dirname(__file__), file_name)
            with open(file_path, "r", encoding="utf-8") as setting_file:
                setting = json.loads(setting_file.read())[setting_name]
        except KeyError as e:
            if default != _default_sentinel:
                return default
            raise e
    return setting
