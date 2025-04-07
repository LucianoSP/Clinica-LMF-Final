# Configuração de logging para o backend
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s:%(name)s: %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "level": "INFO",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "formatter": "detailed",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/backend.log",
            "level": "DEBUG",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    },
    "loggers": {
        "backend": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        },
        "backend.repositories": {
            "level": "INFO",
            "propagate": True
        },
        "backend.routes": {
            "level": "INFO",
            "propagate": True
        },
        "backend.services": {
            "level": "INFO",
            "propagate": True
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO"
    }
} 