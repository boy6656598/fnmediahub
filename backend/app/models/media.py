from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger
from sqlalchemy.sql import func
from app.core.database import Base


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    share_link_id = Column(Integer, nullable=True)
    title = Column(String(500), nullable=False)
    title_cn = Column(String(500), nullable=True)
    poster_url = Column(Text, nullable=True)
    backdrop_url = Column(Text, nullable=True)
    media_type = Column(String(20), nullable=False, default="movie")
    year = Column(Integer, nullable=True)
    overview = Column(Text, nullable=True)
    tmdb_id = Column(String(50), nullable=True)
    douban_id = Column(String(50), nullable=True)
    file_path = Column(Text, nullable=True)
    file_size = Column(BigInteger, nullable=True)
    status = Column(String(20), default="pending")
    play_position = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
