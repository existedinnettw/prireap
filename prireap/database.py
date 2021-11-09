from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
#https://docs.sqlalchemy.org/en/14/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.asyncpg
PG_DRIVER='psycopg2' #psycopg2,asyncpg
DB_URL="postgresql+{}://{}:{}@{}:{}/{}".format(
    PG_DRIVER,
    os.getenv('DB_USR'),
    os.getenv('DB_PWD'),
    os.getenv('DB_HOST'),
    os.getenv('DB_PORT'),
    os.getenv('DB_NAME')
) #os.getenv('DB_URL')
engine = create_engine(
    DB_URL,
    #connect_args={"check_same_thread": False} #only need for sqlite
    # pool_size=20, max_overflow=0,
    # echo=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()