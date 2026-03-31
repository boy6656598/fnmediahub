from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class STRMFile(Base):
    __tablename__ = "strm_files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    media_id = Column(Integer, ForeignKey("media.id"), nullable=True)
    file_path = Column(String(1000), nullable=False)
    file_url = Column(Text, nullable=True)
    episode = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
