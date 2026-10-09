import pytest
from crypto_core import *
from qr_io import make_qr, png_bytes, scan_qr

def test_roundtrip():
    p = encrypt("Meet me at 5 PM", "k3y!")
    assert decrypt(p, "k3y!") == "Meet me at 5 PM"

def test_unicode():
    m = "गुप्त संदेश 🔐"
    assert decrypt(encrypt(m, "pw"), "pw") == m

def test_wrong_key():
    with pytest.raises(DecryptionError): decrypt(encrypt("x", "a"), "b")

def test_tamper():
    p = encrypt("hello world", "a")
    head, b = p.split(".")
    b = b[:-3] + ("AAA" if b[-3:] != "AAA" else "BBB")
    with pytest.raises(DecryptionError): decrypt(head + "." + b, "a")

def test_unique():
    assert encrypt("same", "k") != encrypt("same", "k")

def test_garbage():
    for g in ["hello", "QRSM1.@@@", "QRSM1.AAAA"]:
        with pytest.raises(DecryptionError): decrypt(g, "k")

def test_qr_scan_roundtrip():
    p = encrypt("Meet me at 5 PM behind the library. " * 4, "pw")
    assert scan_qr(png_bytes(make_qr(p))) == p
    assert decrypt(scan_qr(png_bytes(make_qr(p))), "pw").startswith("Meet")
