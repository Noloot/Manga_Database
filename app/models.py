from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import date, datetime, timezone
from typing import List
import uuid

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Manga(Base):
    __tablename__ = 'manga'
    
    id: Mapped[str] = mapped_column(db.String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(db.String(350), nullable=False)
    author: Mapped[str] = mapped_column(db.String(350), nullable=False)
    status: Mapped[str] = mapped_column(db.String(350), nullable=False)
    cover_url: Mapped[str] = mapped_column(db.String(350), nullable=False)
    genre: Mapped[str] = mapped_column(db.String(1000), nullable=False)
    book_type: Mapped[str] = mapped_column(db.String(350), nullable=False)
    published_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    rating: Mapped[float] = mapped_column(db.Float(), nullable=False)
    views: Mapped[int] = mapped_column(db.Integer, nullable=False)
    description: Mapped[str] = mapped_column(db.Text(10000), nullable=True)
    
class User(Base):
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(100), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(db.String(500), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(db.Text, nullable=False)
    role: Mapped[str] = mapped_column(db.String(50), default="user")
    
class Bookmark(Base):
    __tablename__ = 'bookmark'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'manga_id', name='unique_user_bookmark'),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'), nullable=False)
    manga_id: Mapped[str] = mapped_column(db.ForeignKey('manga.id'), nullable=False)
    favorited: Mapped[bool] = mapped_column(db.Boolean, default=False)
    added_at: Mapped[datetime] = mapped_column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_read_chapter: Mapped[str] = mapped_column(db.String(500))
    last_updated: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    
    user = relationship("User", backref="bookmarks")
    
class ReadingHistory(Base):
    __tablename__ = 'reading_history'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'manga_id', name='unique_user_history'),
    )

    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'), nullable=False)
    manga_id: Mapped[str] = mapped_column(db.ForeignKey('manga.id'), nullable=False)
    last_chapter: Mapped[str] = mapped_column(db.String(500), nullable=True)
    last_read_at: Mapped[datetime] = mapped_column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
class Chapter(Base):
    __tablename__ = 'chapter'
    
    id: Mapped[str] = mapped_column(db.String(500), primary_key=True, default=lambda: str(uuid.uuid4()))
    manga_id: Mapped[str] = mapped_column(db.ForeignKey('manga.id'), nullable=False)
    chapter_number: Mapped[str] = mapped_column(db.String(50), nullable=False)
    title: Mapped[str] = mapped_column(db.String(500), nullable=True)
    release_date: Mapped[datetime] = mapped_column(db.DateTime, nullable=False)
    language: Mapped[str] = mapped_column(db.String(50), default='en')
    
    manga = relationship("Manga", backref="chapters")
    
class Download(Base):
    __tablename__ = 'download'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'), nullable=False)
    chapter_id: Mapped[str] = mapped_column(db.ForeignKey('chapter.id'), nullable=False)
    downloaded_at: Mapped[datetime] = mapped_column(db.DateTime, default=lambda: datetime.now(timezone.utc))