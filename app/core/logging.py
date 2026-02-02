import logging


def setup_logging(level: int = logging.INFO):
    """Basic logging setup. Customize in production as needed."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


logger = logging.getLogger("healthcare_booking_agent")
setup_logging()
