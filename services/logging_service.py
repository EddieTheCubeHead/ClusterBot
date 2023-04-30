import os
import sys
from logging import FileHandler, Formatter, StreamHandler, INFO, Handler, Logger, DEBUG, WARNING, ERROR, CRITICAL, \
    getLogger

from discord.utils import stream_supports_colour

from configuration.configuration_service import get_config

_LOG_LEVELS = {
    "DEBUG": DEBUG,
    "INFO": INFO,
    "WARNING": WARNING,
    "ERROR": ERROR,
    "CRITICAL": CRITICAL
}

_LOG_STREAMS = {
    "stdout": sys.stdout,
    "stderr": sys.stderr
}

_FILE_HANDLERS: dict[str, FileHandler] = {}


class LoggingConfiguration:

    def __init__(self, log_file: str, log_stream: str, log_level: str):
        self.log_file = log_file
        self.log_stream = _LOG_STREAMS.get(log_stream, None)
        self.log_level = _LOG_LEVELS[log_level]


def _build_configuration_from_config(log_type: str) -> LoggingConfiguration:
    log_file = get_config(f"{log_type}_LOG_FILE")
    log_stream = get_config(f"{log_type}_LOG_STREAM")
    log_level = get_config(f"{log_type}_LOG_LEVEL")
    return LoggingConfiguration(log_file, log_stream, log_level)


def _get_formatter(handler: Handler) -> Formatter:
    if not isinstance(handler, FileHandler):
        if isinstance(handler, StreamHandler) and stream_supports_colour(handler.stream):
            return _ColourFormatter()
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    return Formatter("{asctime} {levelname:<8} {name:<24} {message}", dt_fmt, style="{")


def _ensure_file(file_name: str):
    with open(file_name, "w") as _:
        pass


def _get_file_handler(file_name: str) -> FileHandler:
    if file_name not in _FILE_HANDLERS:
        _ensure_file(file_name)
        _FILE_HANDLERS[file_name] = FileHandler(file_name)
    return _FILE_HANDLERS[file_name]


def _build_logger(log_type: str):
    log_config = _build_configuration_from_config(log_type)
    stream_handler = None
    if log_config.log_stream is not None:
        stream_handler = StreamHandler(log_config.log_stream)
        stream_handler.setFormatter(_get_formatter(stream_handler))
    file_handler = None
    if log_config.log_file is not None:
        file_handler = _get_file_handler(log_config.log_file)
        file_handler.setFormatter(_get_formatter(file_handler))
    logger = getLogger(log_type.lower())
    logger.setLevel(log_config.log_level)
    if stream_handler is not None:
        logger.addHandler(stream_handler)
    if file_handler is not None:
        logger.addHandler(file_handler)


def setup_logging():
    _build_logger("BOT")
    _build_logger("DISCORD")
    getLogger("bot.logging").info("Logging set up successfully")


# The following code is "borrowed" and modified a little from discord.py to standardize bot logging and discord
# logging formatting:

class _ColourFormatter(Formatter):

    # ANSI codes are a bit weird to decipher if you're unfamiliar with them, so here's a refresher
    # It starts off with a format like \x1b[XXXm where XXX is a semicolon separated list of commands
    # The important ones here relate to colour.
    # 30-37 are black, red, green, yellow, blue, magenta, cyan and white in that order
    # 40-47 are the same except for the background
    # 90-97 are the same but "bright" foreground
    # 100-107 are the same as the bright ones but for the background.
    # 1 means bold, 2 means dim, 0 means reset, and 4 means underline.

    LEVEL_COLOURS = [
        (DEBUG, '\x1b[40;1m'),
        (INFO, '\x1b[34;1m'),
        (WARNING, '\x1b[33;1m'),
        (ERROR, '\x1b[31m'),
        (CRITICAL, '\x1b[41m'),
    ]

    FORMATS = {
        level: Formatter(
            f'\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[35m%(name)-24s\x1b[0m %(message)s',
            '%Y-%m-%d %H:%M:%S',
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output
