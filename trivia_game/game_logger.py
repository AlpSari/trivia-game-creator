import logging
import colorlog


def create_logger(name, logging_level_str='critical'):
    # # Log some messages
    # logging.debug('This is a debug message')
    # logging.info('This is an info message')
    # logging.critical('This is a critical message')

    logger = logging.getLogger(name)  # Create a logger instance
    # Set the logging level
    if logging_level_str in ['none', 'critical']:
        logger.setLevel(logging.CRITICAL + 1)
    elif logging_level_str in ['info']:
        logger.setLevel(logging.INFO)
    elif logging_level_str in ['debug']:
        logger.setLevel(logging.DEBUG)
    else:
        raise (KeyError('Check logging_level_str'))

    # Give Output to Console (Standard Output)
    # Create a color formatter
    formatter = colorlog.ColoredFormatter(
        '%(log_color)s %(name)s: [%(levelname)s] - %(message)s',
        log_colors={
            'DEBUG': 'reset',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
