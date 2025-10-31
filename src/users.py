from pathlib import Path
from typing import Optional
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "Users"
    user_id: Mapped[int] = mapped_column(unique=True)
    chapter: Mapped[Optional[int]]

engine = None

baseDir = Path(__file__).resolve().parents[1]
dataDir = baseDir / "data"

def init_users_db():
    global dataDir
    global engine

    if not dataDir.exists():
        dataDir.mkdir(parents=True, exist_ok=True)

    db_path = dataDir / "data.db"

    engine = create_engine(f"sqlite:///{db_path}", echo=False)

    Base.metadata.create_all(engine)

    return engine


def add_user_in_db(user_id: int , chapter: int | None = None) -> bool:
    try:
        with Session(engine) as session:
            user_n = User(
                user_id=user_id,
                chapter=chapter
            )
            session.add(user_n)
            session.commit()

            stmt = select(User).where(User.id.is_(user_n.id))

            for user_n in session.scalars(stmt):
                print(user_n.user_id)
        return True
    except:
        return False