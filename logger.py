"""
WARNING: dont use loguru, use structlog
https://gist.github.com/nkhitrov/38adbb314f0d35371eba4ffb8f27078f
Configure handlers and formats for application loggers.
"""
import logging
import sys
from pprint import pformat

# if you dont like imports of private modules
# you can move it to typing.py module
from loguru import logger
from loguru._defaults import LOGURU_FORMAT


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentaion.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_record(record: dict) -> str:
    """
    Custom format for loguru loggers.
    Uses pformat for log any data like request/response body during debug.
    Works with logging if loguru handler it.
    Example:
    >>> payload = [{"users":[{"name": "Nick", "age": 87, "is_active": True}, {"name": "Alex", "age": 27, "is_active": True}], "count": 2}]
    >>> logger.bind(payload=).debug("users payload")
    >>> [   {   'count': 2,
    >>>         'users': [   {'age': 87, 'is_active': True, 'name': 'Nick'},
    >>>                      {'age': 27, 'is_active': True, 'name': 'Alex'}]}]
    """

    format_string = LOGURU_FORMAT
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"
    return format_string


def init_logging():
    """
    Replaces logging handlers with a handler for using the custom handler.
        
    WARNING!
    if you call the init_logging in startup event function, 
    then the first logs before the application start will be in the old format
    >>> app.add_event_handler("startup", init_logging)
    stdout:
    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [11528] using statreload
    INFO:     Started server process [6036]
    INFO:     Waiting for application startup.
    2020-07-25 02:19:21.357 | INFO     | uvicorn.lifespan.on:startup:34 - Application startup complete.
    
    """

    intercept_handler = InterceptHandler()

    # disable handlers for specific uvicorn loggers
    # to redirect their output to the default uvicorn logger
    # works with uvicorn==0.11.6
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("uvicorn.") or name.startswith("gunicorn.")
    )
    for uvicorn_logger in loggers:
        uvicorn_logger.handlers = [intercept_handler]

    # change handler for default uvicorn logger
    # logging.getLogger("uvicorn.error").handlers = [intercept_handler]
    # logging.getLogger("uvicorn.access").handlers = [intercept_handler]
    # logging.getLogger("gunicorn.error").handlers = [intercept_handler]
    # logging.getLogger("gunicorn.access").handlers = [intercept_handler]

    # set logs output, level and format
    logger.add(sys.stdout, level=logging.DEBUG)
    logger.add("logs/main.log", enqueue=True, rotation="04:06", level=logging.DEBUG)     # New file is created each day at noon
