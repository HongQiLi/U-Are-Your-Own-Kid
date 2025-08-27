from sqlmodel import SQLModel, Session, create_engine
from utils.config import settings  # 如果你叫 utils/settings.py，就改成 from utils.settings import settings

engine = create_engine(settings.DATABASE_URL, echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
