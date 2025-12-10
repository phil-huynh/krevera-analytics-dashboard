from sqlalchemy import Column, BigInteger, String, Boolean, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.core.database import Base


class Defect(Base):
    __tablename__ = "defects"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    defect_type = Column(String(50), nullable=False, index=True)
    reject = Column(Boolean, nullable=False, default=False, index=True)
    pixel_severity_value = Column(Numeric(10, 6), nullable=True)
    pixel_severity_reject = Column(Boolean, nullable=True)
    threshold = Column(Numeric(10, 6), nullable=True)
    min_value = Column(Numeric(10, 6), nullable=True, default=0.0)
    max_value = Column(Numeric(10, 6), nullable=True, default=1.0)

    product = relationship("Product", back_populates="defects")

    __table_args__ = (
        Index('idx_defects_type_reject', 'defect_type', 'reject'),
        Index('idx_defects_severity', 'pixel_severity_value'),
        Index('idx_defects_product_type', 'product_id', 'defect_type'),
    )

    def __repr__(self) -> str:
        return (
            f"<Defect(id={self.id}, "
            f"product_id={self.product_id}, "
            f"type={self.defect_type}, "
            f"reject={self.reject}, "
            f"severity={self.pixel_severity_value})>"
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "defect_type": self.defect_type,
            "reject": self.reject,
            "pixel_severity": {
                "value": float(self.pixel_severity_value) if self.pixel_severity_value else None,
                "reject": self.pixel_severity_reject,
                "threshold": float(self.threshold) if self.threshold else None,
                "min_value": float(self.min_value) if self.min_value else None,
                "max_value": float(self.max_value) if self.max_value else None,
            }
        }