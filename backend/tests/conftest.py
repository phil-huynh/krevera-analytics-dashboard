import pytest
import os
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import random

from app.main import app
from app.core.database import Base, get_db
from app.models import Product, MachineState, Defect


TEST_DATABASE_URL = "sqlite:///:memory:"

# Global ID counters for SQLite (which doesn't auto-increment BigInteger)
_product_id_counter = 0
_machine_state_id_counter = 0
_defect_id_counter = 0


def get_next_product_id():
    global _product_id_counter
    _product_id_counter += 1
    return _product_id_counter


def get_next_machine_state_id():
    global _machine_state_id_counter
    _machine_state_id_counter += 1
    return _machine_state_id_counter


def get_next_defect_id():
    global _defect_id_counter
    _defect_id_counter += 1
    return _defect_id_counter


def reset_id_counters():
    global _product_id_counter, _machine_state_id_counter, _defect_id_counter
    _product_id_counter = 0
    _machine_state_id_counter = 0
    _defect_id_counter = 0


@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    reset_id_counters()

    yield engine

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_product(db_session) -> Product:
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
    db_session.refresh(product)
    return product


@pytest.fixture
def sample_machine_state(db_session, sample_product) -> MachineState:
    machine_state = MachineState(
        id=get_next_machine_state_id(),
        product_id=sample_product.id,
        cycle_time=25.5,
        shot_count=1000,
    )
    db_session.add(machine_state)
    db_session.commit()
    db_session.refresh(machine_state)
    return machine_state


@pytest.fixture
def sample_defect(db_session, sample_product) -> Defect:
    defect = Defect(
        id=get_next_defect_id(),
        product_id=sample_product.id,
        defect_type="flash_defect",
        pixel_severity_value=0.75,
        pixel_severity_reject=True,
        reject=True,
    )
    db_session.add(defect)
    db_session.commit()
    db_session.refresh(defect)
    return defect


@pytest.fixture
def populated_db(db_session) -> Session:
    base_timestamp = datetime.now() - timedelta(days=30)
    machines = ["molding-machine-1", "molding-machine-2", "molding-machine-3"]
    defect_types = [
        "flash_defect",
        "short_defect",
        "discoloration_defect",
        "burn_mark_defect",
        "contamination_defect",
    ]

    for i in range(100):
        product = Product(
            id=get_next_product_id(),
            version="1.0",
            timestamp=base_timestamp + timedelta(hours=i),
            molding_machine_id=random.choice(machines),
            overall_reject=random.choice([True, False]),
            defect_count=random.randint(0, 3),
            total_severity_score=random.uniform(0, 3.0),
        )
        db_session.add(product)
        db_session.flush()

        machine_state = MachineState(
            id=get_next_machine_state_id(),
            product_id=product.id,
            cycle_time=random.uniform(20.0, 35.0),
            shot_count=random.randint(500, 2000),
        )
        db_session.add(machine_state)

        defect_count = product.defect_count
        if defect_count > 0:
            for _ in range(defect_count):
                defect = Defect(
                    id=get_next_defect_id(),
                    product_id=product.id,
                    defect_type=random.choice(defect_types),
                    pixel_severity_value=random.uniform(0.1, 1.0),
                    pixel_severity_reject=random.choice([True, False]),
                    reject=random.choice([True, False]),
                )
                db_session.add(defect)

    db_session.commit()
    return db_session


@pytest.fixture
def mock_s3_service(monkeypatch):
    class MockS3Service:
        def __init__(self):
            self.uploaded_files = {}
            self._s3_client = None

        @property
        def s3_client(self):
            return self._s3_client

        @property
        def bucket_name(self):
            return "test-bucket"

        def upload_file(self, file_content: bytes, object_key: str) -> str:
            self.uploaded_files[object_key] = file_content
            return f"s3://test-bucket/{object_key}"

        def download_file(self, object_key: str) -> bytes:
            if object_key not in self.uploaded_files:
                raise Exception("File not found")
            return self.uploaded_files[object_key]

        def file_exists(self, object_key: str) -> bool:
            return object_key in self.uploaded_files

        def get_s3_uri(self, object_key: str) -> str:
            return f"s3://test-bucket/{object_key}"

    mock_service = MockS3Service()
    monkeypatch.setattr("app.services.s3_service.s3_service", mock_service)
    monkeypatch.setattr("app.workflows.activities.s3_service", mock_service)
    return mock_service