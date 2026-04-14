import logging

from groot.chat.infrastructure.persistence.base import Base
from groot.chat.infrastructure.persistence.session import engine

logger = logging.getLogger(__name__)


def init_db() -> None:
    logger.info("Initializing database schema")
    Base.metadata.create_all(bind=engine)
