import base64
import hashlib
import secrets

from cryptography.fernet import Fernet
from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def new_raw_token() -> str:
    return secrets.token_urlsafe(32)


def _fernet() -> Fernet:
    digest = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_secret(value: str) -> str:
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_secret(value: str) -> str:
    return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")


def sign_user(user_id, salt: str) -> str:
    return TimestampSigner(salt=salt).sign(str(user_id))


def unsign_user(token: str, salt: str, max_age: int) -> str | None:
    try:
        return TimestampSigner(salt=salt).unsign(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
