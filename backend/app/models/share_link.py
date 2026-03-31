from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger
from sqlalchemy.sql import func
from app.core.database import Base


class ShareLink(Base):
    __tablename__ = "share_links"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    url = Column(Text, nullable=False)
    status = Column(String(20), default="pending")
    extracted_info = Column(Text, nullable=True)
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def set_extracted_info(self, info: dict):
        import json
        self.extracted_info = json.dumps(info)

    def get_extracted_info(self) -> dict:
        import json
        return json.loads(self.extracted_info) if self.extracted_info else {}
