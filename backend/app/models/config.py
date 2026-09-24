from sqlalchemy import Column, Integer, Numeric
from app.core.db import Base
from app.models.base import CommonMixin


class SystemConfig(CommonMixin, Base):
    __tablename__ = "system_config"

    risk_low_max_minutes = Column(Numeric(5, 2), nullable=False, default=5.0)
    risk_medium_max_minutes = Column(Numeric(5, 2), nullable=False, default=15.0)
    turnaround_buffer_minutes = Column(Integer, nullable=False, default=15)
    optimizer_timeout_seconds = Column(Integer, nullable=False, default=60)
    optimizer_weight_delay_cost = Column(Numeric(6, 2), nullable=False, default=1.0)
    optimizer_weight_conflict_cost = Column(Numeric(6, 2), nullable=False, default=50.0)
    optimizer_weight_reassignment_cost = Column(Numeric(6, 2), nullable=False, default=5.0)
    optimizer_weight_taxi_distance = Column(Numeric(6, 2), nullable=False, default=0.1)
    optimizer_weight_remote_stand = Column(Numeric(6, 2), nullable=False, default=10.0)
    cascade_max_depth = Column(Integer, nullable=False, default=5)
