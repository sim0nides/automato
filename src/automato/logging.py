import logging

default_handler = logging.StreamHandler()
default_handler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
)


def create_logger(debug: bool | None = None) -> logging.Logger:
    logger = logging.getLogger()

    if debug:
        logger.setLevel(logging.DEBUG)

    logger.addHandler(default_handler)

    return logger
