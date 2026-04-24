import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from shared.config.settings import settings

logger = logging.getLogger(__name__)

database_url = (
    "postgresql+psycopg://"
    f"{settings.database_username}:{settings.database_password}"
    f"@{settings.database_host}:{settings.database_port}/{settings.database_name}"
)

engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def get_session() -> Session:
    logger.debug("Creating database session")
    return SessionLocal()
