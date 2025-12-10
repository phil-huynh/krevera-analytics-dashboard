from sqlalchemy import Column, BigInteger, Integer, Numeric, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.core.database import Base


class MachineState(Base):
    __tablename__ = "machine_states"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)

    cycle_time = Column(Numeric(10, 3), nullable=True)
    vtop_time = Column(Numeric(10, 3), nullable=True)
    charge_time = Column(Numeric(10, 3), nullable=True)
    cool_time_sp = Column(Numeric(10, 3), nullable=True)
    inj_time_sp = Column(Numeric(10, 3), nullable=True)
    clamp_open_time_cv = Column(Numeric(10, 3), nullable=True)
    clamp_close_time_cv = Column(Numeric(10, 3), nullable=True)
    ej_fwd_time_cv = Column(Numeric(10, 3), nullable=True)
    ej_ret_time_cv = Column(Numeric(10, 3), nullable=True)
    vp_transfer_time_sp = Column(Numeric(10, 3), nullable=True)
    hold_segment_1_time_sp = Column(Numeric(10, 3), nullable=True)
    hold_segment_2_time_sp = Column(Numeric(10, 3), nullable=True)
    hold_segment_3_time_sp = Column(Numeric(10, 3), nullable=True)
    hold_segment_4_time_sp = Column(Numeric(10, 3), nullable=True)

    inj_peak_pressure = Column(Numeric(10, 2), nullable=True)
    fill_peak_press = Column(Numeric(10, 2), nullable=True)
    vtop_press = Column(Numeric(10, 2), nullable=True)
    hold_segment_1_pressure_sp = Column(Numeric(10, 2), nullable=True)
    hold_segment_2_pressure_sp = Column(Numeric(10, 2), nullable=True)
    hold_segment_3_pressure_sp = Column(Numeric(10, 2), nullable=True)
    hold_segment_4_pressure_sp = Column(Numeric(10, 2), nullable=True)
    hold_segment_5_pressure_sp = Column(Numeric(10, 2), nullable=True)
    fill_segment_1_pressure_sp = Column(Numeric(10, 2), nullable=True)
    fill_segment_2_pressure_sp = Column(Numeric(10, 2), nullable=True)
    fill_segment_3_pressure_sp = Column(Numeric(10, 2), nullable=True)
    fill_segment_4_pressure_sp = Column(Numeric(10, 2), nullable=True)
    fill_segment_5_pressure_sp = Column(Numeric(10, 2), nullable=True)
    clamp_force_sp = Column(BigInteger, nullable=True)
    tonnage_force_cv = Column(BigInteger, nullable=True)

    barrel_1 = Column(Numeric(10, 2), nullable=True)
    barrel_2 = Column(Numeric(10, 2), nullable=True)
    barrel_3 = Column(Numeric(10, 2), nullable=True)
    barrel_4 = Column(Numeric(10, 2), nullable=True)
    barrel_5 = Column(Numeric(10, 2), nullable=True)
    barrel_6 = Column(Numeric(10, 2), nullable=True)
    barrel_n1 = Column(Numeric(10, 2), nullable=True)
    barrel_n2 = Column(Numeric(10, 2), nullable=True)
    h1_temp_sp = Column(Numeric(10, 2), nullable=True)
    h2_temp_sp = Column(Numeric(10, 2), nullable=True)
    h3_temp_sp = Column(Numeric(10, 2), nullable=True)
    h4_temp_sp = Column(Numeric(10, 2), nullable=True)
    h5_temp_sp = Column(Numeric(10, 2), nullable=True)
    h6_temp_sp = Column(Numeric(10, 2), nullable=True)
    n1_temp_sp = Column(Numeric(10, 2), nullable=True)
    n2_temp_sp = Column(Numeric(10, 2), nullable=True)

    inj_start_pos = Column(Numeric(10, 2), nullable=True)
    vtop_pos = Column(Numeric(10, 2), nullable=True)
    vp_transfer_position_sp = Column(Numeric(10, 2), nullable=True)
    cushion_min = Column(Numeric(10, 3), nullable=True)
    cushion_fin = Column(Numeric(10, 3), nullable=True)

    fill_segment_1_sp = Column(Numeric(10, 2), nullable=True)
    fill_segment_2_sp = Column(Numeric(10, 2), nullable=True)
    fill_segment_3_sp = Column(Numeric(10, 2), nullable=True)
    fill_segment_4_sp = Column(Numeric(10, 2), nullable=True)
    fill_segment_5_sp = Column(Numeric(10, 2), nullable=True)
    fill_segment_xfer_1_to_2_sp = Column(Numeric(10, 2), nullable=True)
    fill_segment_xfer_2_to_3_sp = Column(Numeric(10, 2), nullable=True)
    fill_segment_xfer_3_to_4_sp = Column(Numeric(10, 2), nullable=True)
    fill_segment_xfer_4_to_5_sp = Column(Numeric(10, 2), nullable=True)

    shot_count = Column(Integer, nullable=True)
    shot_size_sp = Column(Numeric(10, 2), nullable=True)
    pull_back_before_sp = Column(Numeric(10, 2), nullable=True)
    pull_back_after_sp = Column(Numeric(10, 2), nullable=True)

    buzzer_alarm = Column(Boolean, nullable=True, default=False)
    alarm_led = Column(Boolean, nullable=True, default=False)
    cycle_stop_fault = Column(Boolean, nullable=True, default=False)

    product = relationship("Product", back_populates="machine_state")

    __table_args__ = (
        Index('idx_machine_states_cycle_time', 'cycle_time'),
        Index('idx_machine_states_shot_count', 'shot_count'),
        Index('idx_machine_states_barrel_temps', 'barrel_1', 'barrel_2', 'barrel_3'),
    )

    def __repr__(self) -> str:
        return (
            f"<MachineState(id={self.id}, "
            f"product_id={self.product_id}, "
            f"cycle_time={self.cycle_time}, "
            f"shot_count={self.shot_count})>"
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "cycle_time": float(self.cycle_time) if self.cycle_time else None,
            "charge_time": float(self.charge_time) if self.charge_time else None,
            "shot_count": self.shot_count,
            "inj_peak_pressure": float(self.inj_peak_pressure) if self.inj_peak_pressure else None,
            "fill_peak_press": float(self.fill_peak_press) if self.fill_peak_press else None,
            "barrel_1": float(self.barrel_1) if self.barrel_1 else None,
            "barrel_2": float(self.barrel_2) if self.barrel_2 else None,
            "barrel_3": float(self.barrel_3) if self.barrel_3 else None,
        }