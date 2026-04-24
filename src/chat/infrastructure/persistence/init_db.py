import logging

from chat.infrastructure.persistence.base import Base
from chat.infrastructure.persistence.session import engine

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Initialize database tables."""
    logger.info("Initializing database tables")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully")
