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
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
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

    db_path = dataDir / "users.db"

    engine = create_engine(f"sqlite:///{db_path}", echo=False)

    Base.metadata.create_all(engine)

    return engine


def add_user_in_db(user_id: int, chapter: int | None = None) -> bool:
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
                print(f"{user_n.user_id} in {dataDir}")
        return True
    except:
        return False
    

def update_user_chapter(user_id: int, chapter: int) -> bool:
    try:
        with Session(engine) as session:
            stmt = select(User).where(User.user_id == user_id)
            user = session.scalars(stmt).first()

            if user:
                user.chapter = chapter
            else:
                user = User(
                    user_id=user_id,
                    chapter=chapter
                )
                session.add(user)
            
            session.commit()
            print(f"{user.user_id} : {user.chapter}")
        return True
    except:
        return False
    
def get_user_chapter(user_id: int) -> int:
    with Session(engine) as session:
        stmt = select(User).where(User.user_id == user_id)
        user_chapter = session.scalars(stmt).first()
        if user_chapter:
            return user_chapter.chapter
        return None