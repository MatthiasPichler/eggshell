import logging

TRACE = 5

logging.addLevelName(TRACE, "TRACE")

logging.basicConfig(
    level=logging.WARN,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("eggshell")


def trace(func):
    def wrapper(*args, **kwargs):
        logger.log(
            TRACE,
            f"Calling function: {func.__name__} with: args={args}, kwargs={kwargs}",
        )
        result = func(*args, **kwargs)
        logger.log(TRACE, f"Function {func.__name__} returned: {result}")
        return result

    return wrapper
