from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
from jose import JWTError, jwt
import secrets
import pyotp
import qrcode
import io
import base64
import hashlib
import bcrypt

from app.core.config import settings


# ─── Password ────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """
    Hash password using SHA256 first (to handle long passwords),
    then bcrypt for additional security.
    Bcrypt has a 72-byte limit, so we pre-hash with SHA256.
    """
    # Pre-hash with SHA256 to handle passwords longer than 72 bytes
    # Use digest (32 bytes) instead of hexdigest to stay well under 72-byte limit
    sha256_hash = base64.b64encode(hashlib.sha256(password.encode()).digest()).decode('utf-8')
    # Then hash with bcrypt directly (base64 encoded hash is 44 chars, well under 72-byte limit)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(sha256_hash.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify password by first hashing with SHA256, then comparing with bcrypt hash.
    """
    # Pre-hash with SHA256 to match the hashing process
    # Use digest (32 bytes) instead of hexdigest to stay well under 72-byte limit
    sha256_hash = base64.b64encode(hashlib.sha256(plain.encode()).digest()).decode('utf-8')
    # Then verify with bcrypt
    return bcrypt.checkpw(sha256_hash.encode('utf-8'), hashed.encode('utf-8'))


def validate_password_strength(password: str) -> tuple[bool, str]:
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."
    return True, ""


# ─── JWT Tokens ──────────────────────────────────────────────────────────────

def create_access_token(subject: Union[str, Any], extra: dict = {}) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "access",
        **extra,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: Union[str, Any]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def create_invite_token() -> str:
    return secrets.token_urlsafe(32)


def create_reset_token() -> str:
    return secrets.token_urlsafe(32)


# ─── Two-Factor Auth (TOTP) ──────────────────────────────────────────────────

def generate_totp_secret() -> str:
    return pyotp.random_base32()


def verify_totp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def get_totp_uri(secret: str, email: str) -> str:
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=settings.APP_NAME)


def generate_totp_qr_base64(secret: str, email: str) -> str:
    uri = get_totp_uri(secret, email)
    img = qrcode.make(uri)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()
