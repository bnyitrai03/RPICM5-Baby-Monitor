from logging.config import dictConfig

def setup_logging():
    """Configures the logging for the entire application."""
    
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(asctime)s [%(name)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            # App loggers
            "CameraConfigAPI": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "V4L2Commands": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "CameraManager": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "Camera": {"handlers": ["default"], "level": "INFO", "propagate": False},
            # Uvicorn loggers
            "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": False},
        },
    }
    
    dictConfig(log_config)