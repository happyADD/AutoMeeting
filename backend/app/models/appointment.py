"""Appointment model: 预约记录."""
from sqlalchemy import String, Date, Integer, ForeignKey, DateTime, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from app.db import Base


class Appointment(Base):
    __tablename__ = "appointments"
    # Partial unique index: only one *confirmed* booking per (counselor, date, period, hour).
    # Cancelled appointments are excluded so the same slot can be re-booked after cancellation.
    __table_args__ = (
        Index(
            "uq_counselor_datetime_confirmed",
            "counselor_id",
            "appointment_date",
            "period",
            "hour",
            unique=True,
            sqlite_where=text("status = 'confirmed'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    counselor_id: Mapped[int] = mapped_column(ForeignKey("counselors.id"), nullable=False, index=True)
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period: Mapped[str] = mapped_column(String(16), nullable=False)  # "morning" | "afternoon"
    hour: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(String(512), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(64), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(32), nullable=True)
    contact_email: Mapped[str] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="confirmed", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    counselor = relationship("Counselor", back_populates="appointments", lazy="selectin")
