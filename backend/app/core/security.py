import sys
from pathlib import Path
for _p in Path(__file__).resolve().parents:
    if (_p / 'backend').is_dir() and (_p / 'pyproject.toml').is_file():
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
        break

import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from backend.app.core.config import settings


def hash_password(password: str) -> str:
    """Hash plaintext password using bcrypt with salt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except Exception:
        return None


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" [STANDALONE TEST] Security & Authentication Service Execution")
    print("=" * 70)

    password = "ReviewerPassword123!"
    print(f"[*] Hashing plain password: '{password}'")
    hashed = hash_password(password)
    print(f"[+] Generated bcrypt hash : {hashed}")

    print("\n[*] Testing Password Verification:")
    valid = verify_password(password, hashed)
    invalid = verify_password("WrongPassword!", hashed)
    print(f"    - Correct password check : {valid} (Expected True)")
    print(f"    - Wrong password check   : {invalid} (Expected False)")

    print("\n[*] Testing JWT Access Token Lifecycle:")
    token_data = {"sub": "reviewer-user-id", "email": "reviewer@meridianbay.org", "role": "reviewer"}
    token = create_access_token(token_data)
    print(f"[+] Signed JWT Token: {token[:40]}... (len: {len(token)})")

    decoded = decode_access_token(token)
    print(f"[+] Decoded Payload : {decoded}")

    assert valid is True and invalid is False
    assert decoded["email"] == "reviewer@meridianbay.org"
    print("\n[✓] Security & Authentication module validated successfully!\n")

