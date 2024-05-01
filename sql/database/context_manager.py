from . import db_manager
from contextlib import contextmanager

@contextmanager
def get_db_session():
    try:
        current_session = db_manager.SessionLocal()
        yield current_session
    finally:
        current_session.close()

