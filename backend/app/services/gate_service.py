from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.gate import Gate
from app.models.optimization import GateAssignment
from app.schemas.gate import GateCreate, GateResponse, GateListResponse
from app.core.exceptions import GateNotFoundError


class GateService:
    @staticmethod
    def get_gates(
        db: Session,
        terminal: Optional[str] = None,
        is_available: Optional[bool] = None
    ) -> GateListResponse:
        query = db.query(Gate)
        if terminal:
            query = query.filter(Gate.terminal == terminal)
        if is_available is not None:
            query = query.filter(Gate.is_available == is_available)

        gates = query.order_by(Gate.gate_number.asc()).all()

        items = [GateResponse.model_validate(g) for g in gates]
        return GateListResponse(items=items, total=len(items))

    @staticmethod
    def get_gate_by_id(db: Session, gate_id: int) -> Gate:
        gate = db.query(Gate).filter(Gate.id == gate_id).first()
        if not gate:
            raise GateNotFoundError(gate_id)
        return gate

    @staticmethod
    def create_gate(db: Session, gate_in: GateCreate) -> Gate:
        gate = Gate(**gate_in.model_dump())
        db.add(gate)
        db.commit()
        db.refresh(gate)
        return gate
