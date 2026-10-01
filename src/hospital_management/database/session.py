import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from hospital_management.database.base import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hospital_management.db")
CONNECT_ARGS = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=CONNECT_ARGS)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
	database = SessionLocal()
	try:
		yield database
	finally:
		database.close()


def initialize_database() -> None:
	from hospital_management.database.models import patient  # noqa: F401
	from hospital_management.database.models import staff  # noqa: F401

	Base.metadata.create_all(bind=engine)
