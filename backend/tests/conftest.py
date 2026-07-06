from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.database import get_db
from app.main import app
from app.services.email_service import EmailSender, get_email_sender

settings = get_settings()
# NullPool: each test gets a brand-new physical connection tied to its own event
# loop, avoiding asyncpg connections leaking across pytest-asyncio's per-test loops.
test_engine = create_async_engine(settings.test_database_url, future=True, poolclass=NullPool)


class FakeEmailSender(EmailSender):
    def __init__(self) -> None:
        self.sent: list[dict[str, str]] = []
        self.password_reset_sent: list[dict[str, str]] = []

    async def send_verification_otp(self, to: str, otp: str, expire_minutes: int) -> None:
        self.sent.append({"to": to, "otp": otp, "expire_minutes": str(expire_minutes)})

    async def send_password_reset_otp(self, to: str, otp: str, expire_minutes: int) -> None:
        self.password_reset_sent.append({"to": to, "otp": otp, "expire_minutes": str(expire_minutes)})


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Each test runs inside an outer transaction that is always rolled back,
    so tests never leave data behind even though the app code under test
    calls session.commit(). join_transaction_mode="create_savepoint" makes the
    session's commit()/rollback() operate on a SAVEPOINT nested inside the
    outer transaction instead of ending it."""
    async with test_engine.connect() as connection:
        await connection.begin()
        session = AsyncSession(bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False)

        try:
            yield session
        finally:
            await session.close()
            await connection.rollback()


@pytest_asyncio.fixture
async def fake_email_sender() -> FakeEmailSender:
    return FakeEmailSender()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession, fake_email_sender: FakeEmailSender) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_email_sender] = lambda: fake_email_sender

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


async def register_and_verify_user(
    client: AsyncClient, fake_email_sender: FakeEmailSender, *, email: str, password: str
) -> None:
    register_response = await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert register_response.status_code == 201

    otp = next(entry["otp"] for entry in fake_email_sender.sent if entry["to"] == email)
    verify_response = await client.post("/api/v1/auth/verify-email", json={"email": email, "otp": otp})
    assert verify_response.status_code == 200
