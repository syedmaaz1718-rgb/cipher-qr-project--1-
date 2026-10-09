"""AES-256-GCM message sealing. Payload: QRSM1.<base64url(salt16 | nonce12 | ciphertext+tag16)>"""
import base64, os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidTag

PREFIX = "QRSM1"
ITERATIONS = 600_000
SALT_LEN, NONCE_LEN, TAG_LEN = 16, 12, 16


class DecryptionError(Exception):
    pass


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS)
    return kdf.derive(password.encode("utf-8"))


def encrypt(message: str, password: str) -> str:
    if not message:
        raise ValueError("Message is empty.")
    if not password:
        raise ValueError("Secret key is empty.")
    salt, nonce = os.urandom(SALT_LEN), os.urandom(NONCE_LEN)
    ct = AESGCM(derive_key(password, salt)).encrypt(nonce, message.encode("utf-8"), PREFIX.encode())
    blob = base64.urlsafe_b64encode(salt + nonce + ct).decode().rstrip("=")
    return f"{PREFIX}.{blob}"


def parse(payload: str) -> tuple[bytes, bytes, bytes]:
    payload = payload.strip()
    if not payload.startswith(PREFIX + "."):
        raise DecryptionError("Not a CIPHER·QR payload.")
    b = payload.split(".", 1)[1]
    try:
        raw = base64.urlsafe_b64decode(b + "=" * (-len(b) % 4))
    except Exception:
        raise DecryptionError("Payload is corrupted.")
    if len(raw) < SALT_LEN + NONCE_LEN + TAG_LEN + 1:
        raise DecryptionError("Payload is too short.")
    return raw[:SALT_LEN], raw[SALT_LEN:SALT_LEN + NONCE_LEN], raw[SALT_LEN + NONCE_LEN:]


def decrypt(payload: str, password: str) -> str:
    salt, nonce, ct = parse(payload)
    try:
        return AESGCM(derive_key(password, salt)).decrypt(nonce, ct, PREFIX.encode()).decode("utf-8")
    except InvalidTag:
        raise DecryptionError("Wrong key, or the QR was altered. The authentication tag did not match, so nothing is revealed.")


def anatomy(payload: str) -> dict:
    salt, nonce, ct = parse(payload)
    return {"salt": len(salt), "nonce": len(nonce), "ciphertext": len(ct) - TAG_LEN, "tag": TAG_LEN, "total": len(payload)}


def strength(password: str) -> float:
    if not password:
        return 0.0
    pools = sum([any(c.islower() for c in password) * 26, any(c.isupper() for c in password) * 26,
                 any(c.isdigit() for c in password) * 10, any(not c.isalnum() for c in password) * 32])
    import math
    return min(1.0, len(password) * math.log2(max(pools, 1)) / 70)
