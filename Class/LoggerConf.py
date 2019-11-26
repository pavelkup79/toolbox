#import logging
import logging.config

dictLogConfig = {
        "version": 1,
        "handlers": {
            "fileHandler": {
                "class": "logging.FileHandler",
                "formatter": "MainFormatter",
                "filename": "AutoToolBox.log",
                "level": "DEBUG"
            },
            "console":{
                "class": "logging.StreamHandler",
                "formatter": "ConsoleFormatter",
                "level": "INFO"
                }
        },
        "loggers": {
            "AutoToolBox": {
                "handlers": ["fileHandler","console"],
                "level": "DEBUG",
            }
        },
        "formatters": {
            "MainFormatter": {
                "format": "%(filename)s[LINE:%(lineno)d]# %(levelname)s- %(asctime)s - %(message)s"# - %(name)s
            },
            "ConsoleFormatter" : {
                "format": ">>>%(message)s"
            }
        }
    }


logging.config.dictConfig(dictLogConfig)
#logger = logging.getLogger("AutoToolBox")
#logger.info("AutoToolBox Logger is started ")
