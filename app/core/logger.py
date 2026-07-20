import logging

# Create logger
logger = logging.getLogger("fastapi-app")
logger.setLevel(logging.INFO)

# Prevent duplicate logs
if not logger.handlers:
    # Console handler
    console_handler = logging.StreamHandler()

    # Log format
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )

    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)