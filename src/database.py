"""
Database configuration and initialization
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from src.models import Base
from src.credentials import get_creds

db_creds = None

# from sqlalchemy.ext.declarative import declarative_base
# Base = declarative_base()
if db_creds is None:
    db_user = "postgres"
    db_password = "ramanujan"
    db_name = "postgres"
    db_host = "127.0.0.1"
    db_port = 5432
else:
    db_user = "postgres"
    db_password = "ramanujan"
    db_name = "postgres"
    db_host = "127.0.0.1"
    db_port = 5432

uri_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
# uri_string = "postgresql:///strategy_report"
engine = create_engine(uri_string, pool_size=50)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base.query = db_session.query_property()


def init_db():
    """
    Initialize database
    """
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()

    # noinspection PyUnresolvedReferences
    # pylint: disable=cyclic-import, wrong-import-position, unused-variable
    import src.models

    Base.metadata.create_all(bind=engine)
