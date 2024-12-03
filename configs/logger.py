import logging.config

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s - %(asctime)s: %(message)s (Line: %(lineno)d) - [%(filename)s]",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "logfile.log",
        },
    },
    "loggers": {
        "root": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "my_fastapi_app": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

logging.config.dictConfig(log_config)

logger = logging.getLogger("library_app")
