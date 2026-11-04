import os

from sqlmodel import Session, create_engine

sqlite_url = os.getenv("DATABASE_URL", "sqlite:///./ceramics.db")
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session
