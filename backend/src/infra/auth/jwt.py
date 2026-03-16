import hmac
import hashlib
import base64
import json
import time
import os
from uuid import UUID


def hash_password(password: str) -> str:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt.hex() + ":" + key.hex()


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, key_hex = stored.split(":")
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
        return hmac.compare_digest(key, new_key)
    except (ValueError, AttributeError):
        return False


def create_token(user_id: UUID, email: str, secret: str, expire_days: int = 7) -> str:
    header = _b64encode({"alg": "HS256", "typ": "JWT"})
    payload = _b64encode({
        "sub": str(user_id),
        "email": email,
        "exp": int(time.time()) + expire_days * 86400,
    })
    signature = _sign(f"{header}.{payload}", secret)
    return f"{header}.{payload}.{signature}"


def verify_token(token: str, secret: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token format")

    header, payload, signature = parts
    expected = _sign(f"{header}.{payload}", secret)

    if not hmac.compare_digest(signature, expected):
        raise ValueError("Invalid token signature")

    data = json.loads(base64.urlsafe_b64decode(payload + "=="))
    if data.get("exp", 0) < time.time():
        raise ValueError("Token expired")

    return data


def _b64encode(data: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(data, separators=(",", ":")).encode()).rstrip(b"=").decode()


def _sign(message: str, secret: str) -> str:
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
