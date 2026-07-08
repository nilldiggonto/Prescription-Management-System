from httpx import AsyncClient

from tests.conftest import FakeEmailSender, register_and_verify_user

EMAIL_A = "doctor-a@example.com"
EMAIL_B = "doctor-b@example.com"
PASSWORD = "supersecret123"

PATIENT_PAYLOAD = {
    "full_name": "John Patient",
    "age": 34,
    "gender": "male",
    "phone": "+8801711111111",
    "address": "House 1, Dhaka",
}


async def _login(client: AsyncClient, fake_email_sender: FakeEmailSender, email: str) -> None:
    await register_and_verify_user(client, fake_email_sender, email=email, password=PASSWORD)
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200


async def test_create_and_list_patient(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await _login(client, fake_email_sender, EMAIL_A)
    csrf_token = client.cookies.get("csrf_token")

    create_response = await client.post(
        "/api/v1/patients", json=PATIENT_PAYLOAD, headers={"X-CSRF-Token": csrf_token}
    )
    assert create_response.status_code == 201
    patient_id = create_response.json()["id"]

    list_response = await client.get("/api/v1/patients")
    assert list_response.status_code == 200
    assert any(patient["id"] == patient_id for patient in list_response.json())


async def test_patient_not_visible_to_a_different_doctor(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await _login(client, fake_email_sender, EMAIL_A)
    csrf_token = client.cookies.get("csrf_token")
    create_response = await client.post(
        "/api/v1/patients", json=PATIENT_PAYLOAD, headers={"X-CSRF-Token": csrf_token}
    )
    patient_id = create_response.json()["id"]

    client.cookies.clear()
    await _login(client, fake_email_sender, EMAIL_B)

    get_response = await client.get(f"/api/v1/patients/{patient_id}")
    assert get_response.status_code == 404

    list_response = await client.get("/api/v1/patients")
    assert list_response.json() == []
