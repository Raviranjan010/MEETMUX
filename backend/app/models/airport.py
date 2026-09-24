from sqlalchemy import Column, String, Text, Numeric, Enum, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.models.base import CommonMixin, GUID
from app.models.enums import RunwayStatus


class Airport(CommonMixin, Base):
    __tablename__ = "airports"

    code = Column(String(4), unique=True, nullable=False, index=True)
    name = Column(Text, nullable=False)
    timezone = Column(Text, nullable=False)

    terminals = relationship("Terminal", back_populates="airport", cascade="all, delete-orphan")
    runways = relationship("Runway", back_populates="airport", cascade="all, delete-orphan")
    weather_records = relationship("WeatherRecord", back_populates="airport", cascade="all, delete-orphan")


class Terminal(CommonMixin, Base):
    __tablename__ = "terminals"

    airport_id = Column(GUID(), ForeignKey("airports.id", ondelete="RESTRICT"), nullable=False, index=True)
    code = Column(String(8), nullable=False)
    name = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("airport_id", "code", name="uq_terminals_airport_code"),
    )

    airport = relationship("Airport", back_populates="terminals")
    gates = relationship("Gate", back_populates="terminal", cascade="all, delete-orphan")


class Runway(CommonMixin, Base):
    __tablename__ = "runways"

    airport_id = Column(GUID(), ForeignKey("airports.id", ondelete="RESTRICT"), nullable=False, index=True)
    code = Column(String(8), nullable=False)
    status = Column(Enum(RunwayStatus), nullable=False, default=RunwayStatus.ACTIVE, index=True)
    taxi_base_minutes = Column(Numeric(5, 2), nullable=False)

    __table_args__ = (
        UniqueConstraint("airport_id", "code", name="uq_runways_airport_code"),
    )

    airport = relationship("Airport", back_populates="runways")
    flights = relationship("Flight", back_populates="runway")
