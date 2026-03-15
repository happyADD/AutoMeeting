"""Slot template: 一天内可预约的时段配置 (上午/下午按小时)."""
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class SlotTemplate(Base):
    """Defines bookable hour slots per period. e.g. morning 8-12, afternoon 14-18."""
    __tablename__ = "slot_templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period: Mapped[str] = mapped_column(String(16), nullable=False)  # "morning" | "afternoon"
    hour: Mapped[int] = mapped_column(Integer, nullable=False)  # 8, 9, 10, 11 or 14, 15, 16, 17
