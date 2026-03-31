from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    disk_type = Column(String(50), nullable=False, default="fnnas")
    disk_config = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def set_disk_config(self, config: dict):
        import json
        self.disk_config = json.dumps(config)

    def get_disk_config(self) -> dict:
        import json
        return json.loads(self.disk_config) if self.disk_config else {}
