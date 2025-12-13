from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "postgresql+psycopg2://app_user:app_password@localhost:5432/app_db"
)

metadata = MetaData()
metadata.reflect(bind=engine)

session_maker = sessionmaker(engine)
