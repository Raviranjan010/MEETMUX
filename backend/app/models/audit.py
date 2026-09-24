from sqlalchemy import Column, String, Text, Enum, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from app.core.db import Base
from app.models.base import CommonMixin, GUID
from app.models.enums import AuditAction

JSONType = JSON().with_variant(JSONB, "postgresql")


class AuditRecord(CommonMixin, Base):
    __tablename__ = "audit_records"

    action = Column(Enum(AuditAction), nullable=False, index=True)
    actor = Column(Text, nullable=False, default="operator")
    reference_id = Column(GUID(), nullable=True, index=True)
    details = Column(JSONType, nullable=False)

    __table_args__ = (
        Index("ix_audit_records_action_created", "action", "created_at"),
    )
