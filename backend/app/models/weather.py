from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database.database import Base


class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True, nullable=False, default=datetime.utcnow)
    temperature = Column(Float, nullable=False)           # in Celsius
    wind_speed = Column(Float, nullable=False)            # in knots / km/h
    visibility = Column(Float, nullable=False)            # in km
    precipitation = Column(Float, default=0.0)            # in mm
    weather_condition = Column(String(50), default="Clear") # Clear, Rain, Fog, Thunderstorm, Overcast
