
from .database import SessionLocal

# Dependency
def get_db():
    db=SessionLocal() #creawte new session
    try:
        yield db
    finally:
        db.close()