import logging
import sys
from sqlalchemy import create_engine, MetaData
from databases import Database

import os

# Always on top
sys.path.append("..")
sys.path.append(".")
app_dir = os.path.abspath(os.path.dirname(__file__))
projdir = os.path.abspath(os.path.join(app_dir, "../"))

from .env import DATABASE_URL
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

db = declarative_base()

database = Database(DATABASE_URL)
metadata = MetaData()

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=50,
    max_overflow=100,
    pool_pre_ping=True,
)
metadata.create_all(engine)
DBSession = scoped_session(
    sessionmaker(
        autobegin=True,
        autoflush=False,
        bind=engine,
        join_transaction_mode="rollback_only",
        expire_on_commit=False,
    )
)


def get_scoped_session():
    session = scoped_session(
        sessionmaker(autocommit=False, autoflush=True, bind=engine)
    )
    session.begin()
    return session


global_session = get_scoped_session()


class ScopedSession(object):
    """
    Use this for local session scope.
    Usage:
        with ScopedSession as local_db_session:
           ...
           local_db_session.add(some db obj)
           local_db_session.flush() if you need the ID of your new obj right away
           or:
           some_obj = local_db_session.query(some db model).filter(...
           some_obj.field = some_new_value

    Session will be committed and closed when you fall out of scope.
    Rollback handling can be handled by you, or default to what is "expected".
    """

    def __init__(self, rollback_upon_failure=True):
        self.session = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=True,
                bind=engine,
            )
        )
        self.rollback_upon_failure = rollback_upon_failure

    def __enter__(self):
        self.session.begin()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.session.commit()
        except Exception as e:
            if self.rollback_upon_failure:
                self.session.rollback()
                logging.error(f"Failed to commit db session, rolled back: {e}")
            else:
                logging.error(
                    f"Failed to commit db session, not rolled back, as per your request: {e}"
                )
        finally:
            print("Closing session")
            self.session.close()
            self.session.remove
