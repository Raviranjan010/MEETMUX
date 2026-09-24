from sqlalchemy import Column, String, Boolean, DateTime, Numeric, Enum, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.models.base import CommonMixin, GUID
from app.models.enums import AircraftSizeClass, RouteType, WeatherCondition


class Aircraft(CommonMixin, Base):
    __tablename__ = "aircraft"

    registration = Column(String(16), unique=True, nullable=False, index=True)
    type_code = Column(String(8), nullable=False)
    size_class = Column(Enum(AircraftSizeClass), nullable=False)

    flights = relationship("Flight", back_populates="aircraft")


class Flight(CommonMixin, Base):
    __tablename__ = "flights"

    flight_number = Column(String(8), nullable=False)
    airline = Column(String(4), nullable=False)
    aircraft_id = Column(GUID(), ForeignKey("aircraft.id", ondelete="RESTRICT"), nullable=False, index=True)
    route_type = Column(Enum(RouteType), nullable=False, index=True)
    origin = Column(String(4), nullable=True)
    destination = Column(String(4), nullable=True)
    runway_id = Column(GUID(), ForeignKey("runways.id", ondelete="RESTRICT"), nullable=True, index=True)
    scheduled_arrival = Column(DateTime(timezone=True), nullable=False, index=True)
    scheduled_departure = Column(DateTime(timezone=True), nullable=False)
    actual_arrival = Column(DateTime(timezone=True), nullable=True)
    actual_departure = Column(DateTime(timezone=True), nullable=True)
    is_synthetic = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("flight_number", "scheduled_arrival", name="uq_flights_flight_arrival"),
        Index("ix_flights_arrival_route", "scheduled_arrival", "route_type"),
    )

    aircraft = relationship("Aircraft", back_populates="flights")
    runway = relationship("Runway", back_populates="flights")
    predictions = relationship("Prediction", back_populates="flight", cascade="all, delete-orphan")
    gate_assignments = relationship("GateAssignment", back_populates="flight", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="flight")


class WeatherRecord(CommonMixin, Base):
    __tablename__ = "weather_records"

    airport_id = Column(GUID(), ForeignKey("airports.id", ondelete="RESTRICT"), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    condition = Column(Enum(WeatherCondition), nullable=False)
    wind_speed_kt = Column(Numeric(5, 1), nullable=True)
    visibility_m = Column(Numeric(6, 1), nullable=True)

    __table_args__ = (
        Index("ix_weather_records_airport_time", "airport_id", "recorded_at"),
    )

    airport = relationship("Airport", back_populates="weather_records")
