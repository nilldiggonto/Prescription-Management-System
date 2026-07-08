from httpx import AsyncClient

from tests.conftest import FakeEmailSender, register_and_verify_user

EMAIL = "prescriber@example.com"
PASSWORD = "supersecret123"

DOCTOR_PROFILE_PAYLOAD = {
    "full_name": "Dr. Jane Doe",
    "degrees": "MBBS, FCPS (Medicine)",
    "specialization": "Cardiologist",
    "registration_number": "A-12345",
    "hospital_name": "City General Hospital",
    "chamber_address": "House 1, Road 2, Dhaka",
    "phone": "+8801700000000",
    "signature_url": None,
    "logo_url": None,
}

NEW_PATIENT_PAYLOAD = {
    "full_name": "John Patient",
    "age": 34,
    "gender": "male",
    "phone": "+8801711111111",
    "address": "House 1, Dhaka",
}

MEDICINES_PAYLOAD = [
    {"name": "Paracetamol", "dosage": "500mg", "frequency": "1+1+1", "duration": "5 days", "instructions": "After meal"},
    {"name": "Omeprazole", "dosage": "20mg", "frequency": "1+0+0", "duration": "10 days", "instructions": None},
]


async def _login_with_profile(client: AsyncClient, fake_email_sender: FakeEmailSender) -> str:
    await register_and_verify_user(client, fake_email_sender, email=EMAIL, password=PASSWORD)
    login_response = await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert login_response.status_code == 200

    csrf_token = client.cookies.get("csrf_token")
    profile_response = await client.put(
        "/api/v1/doctor-profile/me", json=DOCTOR_PROFILE_PAYLOAD, headers={"X-CSRF-Token": csrf_token}
    )
    assert profile_response.status_code == 200
    return csrf_token


async def test_create_prescription_requires_doctor_profile(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await register_and_verify_user(client, fake_email_sender, email=EMAIL, password=PASSWORD)
    await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
    csrf_token = client.cookies.get("csrf_token")

    response = await client.post(
        "/api/v1/prescriptions",
        json={"new_patient": NEW_PATIENT_PAYLOAD, "medicines": MEDICINES_PAYLOAD},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 400


async def test_create_prescription_with_new_patient_and_download_pdf(
    client: AsyncClient, fake_email_sender: FakeEmailSender
):
    csrf_token = await _login_with_profile(client, fake_email_sender)

    create_response = await client.post(
        "/api/v1/prescriptions",
        json={
            "new_patient": NEW_PATIENT_PAYLOAD,
            "diagnosis": "Acute gastritis",
            "advice": "Drink plenty of water",
            "follow_up_date": "2026-08-01",
            "medicines": MEDICINES_PAYLOAD,
        },
        headers={"X-CSRF-Token": csrf_token},
    )
    assert create_response.status_code == 201
    body = create_response.json()
    assert body["patient"]["full_name"] == NEW_PATIENT_PAYLOAD["full_name"]
    assert len(body["medicines"]) == 2
    prescription_id = body["id"]

    list_response = await client.get("/api/v1/prescriptions")
    assert list_response.status_code == 200
    assert any(item["id"] == prescription_id for item in list_response.json())

    pdf_response = await client.get(f"/api/v1/prescriptions/{prescription_id}/pdf")
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"] == "application/pdf"
    assert pdf_response.content.startswith(b"%PDF")


async def test_create_prescription_with_existing_patient(client: AsyncClient, fake_email_sender: FakeEmailSender):
    csrf_token = await _login_with_profile(client, fake_email_sender)

    patient_response = await client.post(
        "/api/v1/patients", json=NEW_PATIENT_PAYLOAD, headers={"X-CSRF-Token": csrf_token}
    )
    patient_id = patient_response.json()["id"]

    response = await client.post(
        "/api/v1/prescriptions",
        json={"patient_id": patient_id, "medicines": MEDICINES_PAYLOAD},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 201
    assert response.json()["patient"]["id"] == patient_id


async def test_create_prescription_requires_patient_source(client: AsyncClient, fake_email_sender: FakeEmailSender):
    csrf_token = await _login_with_profile(client, fake_email_sender)

    response = await client.post(
        "/api/v1/prescriptions", json={"medicines": MEDICINES_PAYLOAD}, headers={"X-CSRF-Token": csrf_token}
    )
    assert response.status_code == 422
