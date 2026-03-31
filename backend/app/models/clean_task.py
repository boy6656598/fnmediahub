from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class CleanTask(Base):
    __tablename__ = "clean_tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_type = Column(String(50), nullable=False)
    last_run = Column(DateTime(timezone=True), nullable=True)
    next_run = Column(DateTime(timezone=True), nullable=True)
    config = Column(Text, nullable=True)
    status = Column(String(20), default="idle")

    def set_config(self, config: dict):
        import json
        self.config = json.dumps(config)

    def get_config(self) -> dict:
        import json
        return json.loads(self.config) if self.config else {}
