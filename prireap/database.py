from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

engine = create_engine(
    os.getenv('DB_URL'),
    #connect_args={"check_same_thread": False} #only need for sqlite
    # pool_size=20, max_overflow=0,
    # echo=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()