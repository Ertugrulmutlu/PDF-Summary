import logging

def get_logger(name="PDFLlmLogger", console=False):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        file_handler = logging.FileHandler("app.log", encoding="utf-8", mode="a")
        formatter = logging.Formatter(
            "{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        if console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    return logger
