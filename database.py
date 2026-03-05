import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, event
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.engine import Engine

# Define the database file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'autoclaw.sqlite3')
DATABASE_URL = f"sqlite:///{DB_PATH}"

Base = declarative_base()

class DiscoveredJob(Base):
    """
    Stores jobs discovered during scraping.
    """
    __tablename__ = 'discovered_jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    job_description = Column(Text, nullable=False)
    dedup_hash = Column(String(64), unique=True, nullable=False, index=True)
    status = Column(String(50), default='discovered', nullable=False) # e.g., 'discovered', 'applied', 'skipped'
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationship to ApplicationLog
    application_logs = relationship("ApplicationLog", back_populates="job", cascade="all, delete-orphan")

class ApplicationLog(Base):
    """
    Stores the history of application attempts for a job.
    """
    __tablename__ = 'application_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey('discovered_jobs.id'), nullable=False)
    application_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)
    success = Column(Boolean, nullable=False, default=False)

    # Relationship to DiscoveredJob
    job = relationship("DiscoveredJob", back_populates="application_logs")


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Enables WAL mode for thread safety on SQLite connections.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

# Create the engine
engine = create_engine(DATABASE_URL, echo=False)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Creates all tables in the database.
    """
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at {DB_PATH} with WAL mode.")

def get_session():
    """
    Provides a dependency for database sessions.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

if __name__ == "__main__":
    init_db()
