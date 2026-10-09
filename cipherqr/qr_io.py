import io
import cv2, numpy as np, qrcode
from PIL import Image


def make_qr(payload: str) -> Image.Image:
    q = qrcode.QRCode(border=2, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(payload)
    q.make(fit=True)
    return q.make_image(fill_color="#0b0b0d", back_color="#f2ece0").convert("RGB")


def png_bytes(img: Image.Image) -> bytes:
    b = io.BytesIO(); img.save(b, "PNG"); return b.getvalue()


def scan_qr(data: bytes) -> str | None:
    arr = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if arr is None:
        return None
    det = cv2.QRCodeDetector()
    tries = [arr, cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)]
    h, w = arr.shape[:2]
    for s in (0.5, 1.5, 2.0):
        tries.append(cv2.resize(arr, (int(w * s), int(h * s))))
    for t in tries:
        val, _, _ = det.detectAndDecode(t)
        if val:
            return val
        # add white border (helps tight crops)
        padded = cv2.copyMakeBorder(t, 40, 40, 40, 40, cv2.BORDER_CONSTANT, value=(255, 255, 255) if t.ndim == 3 else 255)
        val, _, _ = det.detectAndDecode(padded)
        if val:
            return val
    return None
