import logging


def get_logger(context: str):
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    return logging.getLogger(context)
