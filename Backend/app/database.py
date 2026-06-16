from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# اتصال MySQL (Laragon)
# DATABASE_URL = "mysql+pymysql://root:@localhost/nutritech"
DATABASE_URL = "sqlite:///./nutritech.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()