import logging
from sqlalchemy.ext.declarative import declarative_base
from db.base import Base
from db.session import engine

# Import all models to ensure they are registered with SQLAlchemy
from models import Organization, User, Team, Service, Incident

logger = logging.getLogger(__name__)

def init_db() -> None:
    """Initialize the database, creating all tables."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise