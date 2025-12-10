from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Integer, Numeric, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    version = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    molding_machine_id = Column(String(50), nullable=False, index=True)
    overall_reject = Column(Boolean, nullable=False, default=False, index=True)
    defect_count = Column(Integer, nullable=False, default=0)
    total_severity_score = Column(Numeric(10, 6), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    machine_state = relationship(
        "MachineState",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan"
    )

    defects = relationship(
        "Defect",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index('idx_products_machine_timestamp', 'molding_machine_id', 'timestamp'),
        Index('idx_products_reject_timestamp', 'overall_reject', 'timestamp'),
    )

    def __repr__(self) -> str:
        return (
            f"<Product(id={self.id}, "
            f"machine={self.molding_machine_id}, "
            f"timestamp={self.timestamp}, "
            f"reject={self.overall_reject})>"
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "version": self.version,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "molding_machine_id": self.molding_machine_id,
            "overall_reject": self.overall_reject,
            "defect_count": self.defect_count,
            "total_severity_score": float(self.total_severity_score) if self.total_severity_score else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }