import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models import Product, MachineState, Defect
from tests.conftest import get_next_product_id, get_next_machine_state_id, get_next_defect_id


@pytest.mark.database
class TestProductModel:
    def test_create_product(self, db_session):
        product = Product(
            id=get_next_product_id(),
            version="1.0",
            timestamp=datetime.now(),
            molding_machine_id="molding-machine-1",
            overall_reject=False,
            defect_count=0,
            total_severity_score=0.0,
        )
        db_session.add(product)
        db_session.commit()

        assert product.id is not None
        assert product.molding_machine_id == "molding-machine-1"
        assert product.overall_reject is False

    def test_product_requires_timestamp(self, db_session):
        product = Product(
            id=get_next_product_id(),
            version="1.0",
            molding_machine_id="molding-machine-1",
            overall_reject=False,
            defect_count=0,
            total_severity_score=0.0,
        )
        db_session.add(product)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_product_default_values(self, db_session):
        product = Product(
            id=get_next_product_id(),
            version="1.0",
            timestamp=datetime.now(),
            molding_machine_id="molding-machine-1",
        )
        db_session.add(product)
        db_session.commit()

        assert product.overall_reject is False
        assert product.defect_count == 0
        assert product.total_severity_score is None

    def test_product_relationship_with_machine_state(self, db_session, sample_product):
        machine_state = MachineState(
            id=get_next_machine_state_id(),
            product_id=sample_product.id,
            cycle_time=25.5,
            shot_count=1000,
        )
        db_session.add(machine_state)
        db_session.commit()

        db_session.refresh(sample_product)
        assert sample_product.machine_state is not None
        assert sample_product.machine_state.cycle_time == 25.5

    def test_product_relationship_with_defects(self, db_session, sample_product):
        defects = [
            Defect(
                id=get_next_defect_id(),
                product_id=sample_product.id,
                defect_type="flash_defect",
                pixel_severity_value=0.5,
                pixel_severity_reject=False,
                reject=False,
            ),
            Defect(
                id=get_next_defect_id(),
                product_id=sample_product.id,
                defect_type="short_defect",
                pixel_severity_value=0.8,
                pixel_severity_reject=True,
                reject=True,
            )
        ]
        for defect in defects:
            db_session.add(defect)
        db_session.commit()

        db_session.refresh(sample_product)
        assert len(sample_product.defects) == 2

    def test_product_cascade_delete(self, db_session, sample_product):
        machine_state = MachineState(
            id=get_next_machine_state_id(),
            product_id=sample_product.id,
            cycle_time=25.5,
            shot_count=1000,
        )
        defect = Defect(
            id=get_next_defect_id(),
            product_id=sample_product.id,
            defect_type="flash_defect",
            pixel_severity_value=0.5,
            pixel_severity_reject=False,
            reject=False,
        )
        db_session.add(machine_state)
        db_session.add(defect)
        db_session.commit()

        product_id = sample_product.id
        db_session.delete(sample_product)
        db_session.commit()

        assert db_session.query(Product).filter_by(id=product_id).first() is None
        assert db_session.query(MachineState).filter_by(product_id=product_id).first() is None
        assert db_session.query(Defect).filter_by(product_id=product_id).first() is None


@pytest.mark.database
class TestMachineStateModel:
    def test_create_machine_state(self, db_session, sample_product):
        machine_state = MachineState(
            id=get_next_machine_state_id(),
            product_id=sample_product.id,
            cycle_time=30.2,
            shot_count=1500,
        )
        db_session.add(machine_state)
        db_session.commit()

        assert machine_state.id is not None
        assert machine_state.product_id == sample_product.id
        assert float(machine_state.cycle_time) == 30.2

    def test_machine_state_requires_product(self, db_session):
        machine_state = MachineState(
            id=get_next_machine_state_id(),
            product_id=99999,
            cycle_time=25.5,
            shot_count=1000,
        )
        db_session.add(machine_state)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_machine_state_nullable_fields(self, db_session, sample_product):
        machine_state = MachineState(
            id=get_next_machine_state_id(),
            product_id=sample_product.id,
        )
        db_session.add(machine_state)
        db_session.commit()

        assert machine_state.cycle_time is None
        assert machine_state.shot_count is None

    def test_machine_state_relationship_with_product(self, db_session, sample_product, sample_machine_state):
        db_session.refresh(sample_machine_state)
        assert sample_machine_state.product is not None
        assert sample_machine_state.product.id == sample_product.id


@pytest.mark.database
class TestDefectModel:
    def test_create_defect(self, db_session, sample_product):
        defect = Defect(
            id=get_next_defect_id(),
            product_id=sample_product.id,
            defect_type="contamination_defect",
            pixel_severity_value=0.65,
            pixel_severity_reject=True,
            reject=True,
        )
        db_session.add(defect)
        db_session.commit()

        assert defect.id is not None
        assert defect.product_id == sample_product.id
        assert defect.defect_type == "contamination_defect"

    def test_defect_requires_product(self, db_session):
        defect = Defect(
            id=get_next_defect_id(),
            product_id=99999,
            defect_type="flash_defect",
            pixel_severity_value=0.5,
            pixel_severity_reject=False,
            reject=False,
        )
        db_session.add(defect)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_defect_default_values(self, db_session, sample_product):
        defect = Defect(
            id=get_next_defect_id(),
            product_id=sample_product.id,
            defect_type="flash_defect",
        )
        db_session.add(defect)
        db_session.commit()

        assert defect.reject is False
        assert defect.pixel_severity_reject is None

    def test_defect_relationship_with_product(self, db_session, sample_product, sample_defect):
        db_session.refresh(sample_defect)
        assert sample_defect.product is not None
        assert sample_defect.product.id == sample_product.id

    def test_multiple_defects_per_product(self, db_session, sample_product):
        defects = [
            Defect(
                id=get_next_defect_id(),
                product_id=sample_product.id,
                defect_type=f"defect_{i}",
                pixel_severity_value=float(i) * 0.1,
                pixel_severity_reject=False,
                reject=False,
            )
            for i in range(5)
        ]
        for defect in defects:
            db_session.add(defect)
        db_session.commit()

        db_session.refresh(sample_product)
        assert len(sample_product.defects) == 5