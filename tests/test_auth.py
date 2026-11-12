import pytest
import httpx
from backend.app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from backend.app.models.user import User
from backend.app.models.document import Document


def test_password_hashing():
    pw = "SuperSecure123!"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_token_lifecycle():
    data = {"sub": "user_123", "email": "test@meridianbay.org"}
    token = create_access_token(data)
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "user_123"
    assert payload["email"] == "test@meridianbay.org"


@pytest.mark.asyncio
async def test_api_login_success(client: httpx.AsyncClient, test_user: User):
    resp = await client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "DoctorPass123!"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["email"] == test_user.email
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_api_login_invalid_password(client: httpx.AsyncClient, test_user: User):
    resp = await client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "WrongPassword!"}
    )
    assert resp.status_code == 401
    assert "Incorrect email or password" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_api_register_user(client: httpx.AsyncClient):
    resp = await client.post(
        "/auth/register",
        json={
            "email": "new_pharmacist@meridianbay.org",
            "password": "PharmacistPass123!",
            "full_name": "Dr. Sarah Lin, PharmD"
        }
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new_pharmacist@meridianbay.org"
    assert data["full_name"] == "Dr. Sarah Lin, PharmD"


@pytest.mark.asyncio
async def test_tenant_isolation(
    client: httpx.AsyncClient,
    test_user: User,
    other_user: User,
    auth_headers: dict,
    db_session
):
    """Asserts that a user cannot access documents belonging to another user (REQ-AUTH-01)."""
    # Create document owned by other_user
    other_doc = Document(
        user_id=other_user.id,
        filename="confidential_summary.docx",
        file_type="docx",
        document_type="primary",
        content_hash="mock_hash_other_123",
        raw_text="Confidential record",
        doc_metadata={}
    )
    db_session.add(other_doc)
    await db_session.commit()

    # Attempt to query other_doc using test_user's credentials
    resp = await client.get(f"/api/documents/{other_doc.id}", headers=auth_headers)
    assert resp.status_code == 403
    assert "Access forbidden" in resp.json()["detail"]
