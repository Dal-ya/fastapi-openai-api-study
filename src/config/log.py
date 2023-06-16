import datetime
import os
import logging
import logging.handlers
from typing import Union
import yaml
from pathlib import Path

CONFIG_PATH = Path.cwd() / 'src' / 'config' / 'log.yml'


class Config:
    def __init__(self, config_file=CONFIG_PATH):
        self.config = self._read_config(config_file)

    # noinspection PyMethodMayBeStatic
    def _read_config(self, config_file: Path) -> Union[None, dict]:
        try:
            with open(config_file, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
            return config

        except FileNotFoundError as err:
            print('FileNotFoundError: ', err)
            return {}

    def get_config_value(self, section: str, key: str, default_value=None) -> str:
        """get a value in a section"""
        return self.config.get(section, {}).get(key, default_value)


LOG_FORMAT = "%(asctime)s [%(levelname)-8s] - %(name)8s.(%(lineno)3d) - %(message)s"
DATE_FMT = "%Y/%m/%d %H:%M:%S"


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FMT))
    return stream_handler


def get_file_handler(log_file: str):
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file, when="d", interval=1, backupCount=0
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FMT))
    return file_handler


def get_log_path_file(cfg: Config) -> tuple:
    return (
        cfg.get_config_value("logging", "path"),
        cfg.get_config_value("logging", "filename"),
    )


def get_log_strategy(cfg: Config) -> int:
    strategies = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    return strategies.get(
        cfg.get_config_value("logging", "level", "info").lower(), logging.INFO
    )


def should_log_to_console(cfg: Config) -> str:
    return cfg.get_config_value("logging", "to_console")


def should_log_to_file(cfg: Config) -> str:
    return cfg.get_config_value("logging", "to_file")


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    conf = Config()
    logger.setLevel(get_log_strategy(conf))

    if should_log_to_console(conf):
        logger.addHandler(get_stream_handler())

    if should_log_to_file(conf):
        log_path, log_filename = get_log_path_file(conf)

        if not os.path.exists(log_path):
            if conf.get_config_value("logging", "create_folder"):
                os.makedirs(log_path, exist_ok=True)
            else:
                print("Logging folder not found. Exiting...")
                exit(-1)

        log_file = os.path.join(log_path, f"{log_filename}.{datetime.date.today()}")
        logger.addHandler(get_file_handler(log_file))

    return logger
