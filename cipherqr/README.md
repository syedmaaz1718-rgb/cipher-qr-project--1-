# CIPHER·QR - QR Code Based Secret Message System

Cryptography course project. The message is encrypted with AES-256-GCM, then packed into a QR code. The receiver scans the QR and enters the key to decrypt. A wrong key or a modified QR is rejected by the GCM authentication tag.

## Run
    pip install -r requirements.txt
    streamlit run app.py
    python -m pytest -q      # crypto + QR round-trip tests

## Design
- Key: PBKDF2-HMAC-SHA256, 600,000 iterations, random 16-byte salt
- Cipher: AES-256-GCM, random 12-byte nonce, "QRSM1" as associated data
- Payload: `QRSM1.` + Base64URL(salt | nonce | ciphertext | tag)
- QR: `qrcode` library (error correction M); scan: OpenCV QRCodeDetector
- Files: `crypto_core.py` (crypto), `qr_io.py` (QR make/scan), `app.py` (Streamlit UI), `test_core.py`
