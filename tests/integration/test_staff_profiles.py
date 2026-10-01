from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from hospital_management.database.base import Base
from hospital_management.database.models.staff import StaffProfile
from hospital_management.database.session import get_db
from hospital_management.main import app

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)


def override_get_db() -> Generator[Session, None, None]:
    database = TestSession()
    try:
        yield database
    finally:
        database.close()


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def receptionist_payload() -> dict[str, object]:
    return {
        "role": "receptionist",
        "full_name": "Asha Rao",
        "email": "asha.rao@example.com",
        "phone": "+1 555 010 2000",
        "profession": "Patient Services Coordinator",
        "area_of_expertise": "Front desk operations",
        "qualification": "BBA Healthcare Administration",
        "years_of_experience": 4,
        "password": "SecurePass123!",
    }


def test_receptionist_can_create_profile_and_password_is_hashed(client: TestClient) -> None:
    response = client.post("/api/profiles", json=receptionist_payload())

    assert response.status_code == 201
    assert response.json()["role"] == "receptionist"
    assert "password" not in response.json()

    with TestSession() as database:
        profile = database.scalar(select(StaffProfile))
        assert profile is not None
        assert profile.password_hash != "SecurePass123!"


def test_doctor_requires_medical_license(client: TestClient) -> None:
    payload = receptionist_payload() | {
        "role": "doctor",
        "profession": "Physician",
        "area_of_expertise": "Cardiology",
    }

    response = client.post("/api/profiles", json=payload)

    assert response.status_code == 422


def test_doctor_can_create_profile_with_medical_license(client: TestClient) -> None:
    payload = receptionist_payload() | {
        "role": "doctor",
        "profession": "Physician",
        "area_of_expertise": "Cardiology",
        "license_number": "MED-102938",
    }

    response = client.post("/api/profiles", json=payload)

    assert response.status_code == 201
    assert response.json()["role"] == "doctor"
    assert response.json()["license_number"] == "MED-102938"


def test_duplicate_email_is_rejected(client: TestClient) -> None:
    payload = receptionist_payload()
    assert client.post("/api/profiles", json=payload).status_code == 201

    response = client.post("/api/profiles", json=payload)

    assert response.status_code == 409


def test_created_profile_can_log_in(client: TestClient) -> None:
    payload = receptionist_payload()
    assert client.post("/api/profiles", json=payload).status_code == 201

    response = client.post(
        "/api/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]
    assert response.json()["profile"]["email"] == payload["email"]


def test_receptionist_can_create_patient_entry(client: TestClient) -> None:
    response = client.post(
        "/api/patients",
        json={
            "full_name": "Mira Khan",
            "age": 36,
            "contact_number": "+1 555 010 3030",
            "address": "120 Lakeview Road",
            "appointment_reason": "Fever and body ache",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"]
    assert data["full_name"] == "Mira Khan"
    assert data["age"] == 36
    assert data["contact_number"] == "+1 555 010 3030"
    assert data["address"] == "120 Lakeview Road"