import time
from datetime import datetime
import streamlit as st
from crypto_core import encrypt, decrypt, DecryptionError, anatomy, strength, ITERATIONS
from qr_io import make_qr, png_bytes, scan_qr

st.set_page_config(page_title="CIPHER·QR", page_icon="🔐", layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif}
.stApp{background:radial-gradient(900px 500px at 85% -10%,rgba(255,92,40,.16),transparent 60%),radial-gradient(700px 500px at -10% 110%,rgba(255,176,60,.07),transparent 60%),#0a0a0c;
background-image:linear-gradient(rgba(255,255,255,.022) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.022) 1px,transparent 1px);background-size:48px 48px}
header[data-testid="stHeader"],#MainMenu,footer{visibility:hidden;height:0}
.block-container{max-width:1280px;padding-top:1.6rem;position:relative}
[class*='st-key-card']{background:linear-gradient(160deg,#141418,#0d0d10);border:1px solid #26262b;border-radius:22px;padding:30px}
h1.hero{font:400 64px/1.02 'Instrument Serif',Georgia,serif;letter-spacing:-.02em;margin:.6rem 0 .5rem;color:#eae4d6;font-weight:400}
h1.hero i{color:#ff5c28}
p.sub{color:#8d887c;font-size:16px;line-height:1.6;max-width:520px;margin-bottom:1.4rem}
.lbl{font:500 11px 'JetBrains Mono',monospace;letter-spacing:.16em;color:#8d887c;margin:.9rem 0 .35rem}
/* tabs as pills */
.stTabs [data-baseweb="tab-list"]{gap:6px!important;align-items:center!important;border-bottom:1px solid #1f1f23;padding-bottom:14px}
.stTabs [data-baseweb="tab-list"]::before{content:'CIPHER·QR';margin-right:auto;font:600 15px 'JetBrains Mono',monospace;letter-spacing:.18em;color:#ff5c28}
.stTabs [data-baseweb="tab"] p{font:500 13px 'JetBrains Mono',monospace!important;letter-spacing:.08em}
.stTabs [data-baseweb="tab"]{font:500 13px 'JetBrains Mono',monospace;letter-spacing:.08em;color:#8d887c;border-radius:99px;padding:8px 18px;height:auto;background:transparent}
.stTabs [aria-selected="true"]{background:#ff5c28!important}.stTabs [aria-selected="true"] p{color:#0a0a0c!important}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none}
/* inputs */
.stTextArea textarea,.stTextInput input{background:#111114!important;border:1px solid #26262b!important;border-radius:14px!important;color:#eae4d6!important;font-size:16px!important}
.stTextArea textarea:focus,.stTextInput input:focus{border-color:#ff5c28!important;box-shadow:0 0 0 1px #ff5c28!important}
.stTextInput input[type=password]{letter-spacing:.2em}
.stButton>button,.stDownloadButton>button{background:#ff5c28;color:#0a0a0c;border:0;border-radius:12px;font:600 13px 'JetBrains Mono',monospace;letter-spacing:.1em;padding:.85rem 1.6rem}
.stButton>button:hover,.stDownloadButton>button:hover{background:#ff7a4d;color:#0a0a0c}
.stDownloadButton>button{background:transparent;color:#eae4d6;border:1px solid #2c2c32}
.stDownloadButton>button:hover{background:#1a1a1e;color:#ff5c28;border-color:#ff5c28}
[data-testid="stFileUploaderDropzone"]{background:#111114;border:1px dashed #33333a;border-radius:14px}
.meter{height:4px;background:#1f1f23;border-radius:9px;overflow:hidden;margin:-4px 0 18px}.meter i{display:block;height:100%;background:linear-gradient(90deg,#ff5c28,#ffb03c)}
.card{background:linear-gradient(160deg,#141418,#0d0d10);border:1px solid #26262b;border-radius:22px;padding:30px}
.card.ok{border-color:#2d5a3a;background:#0f1a13}.card.bad{border-color:#6a2a22;background:#1a0f0d}
.tag{font:600 11px 'JetBrains Mono',monospace;letter-spacing:.16em}
.msg{font:400 32px/1.3 'Instrument Serif',Georgia,serif;margin:16px 0;color:#eae4d6;white-space:pre-wrap;word-break:break-word}
.chip{display:inline-block;font:500 12px 'JetBrains Mono',monospace;padding:7px 13px;border:1px solid #2c2c32;border-radius:99px;color:#b9b3a5;margin:0 8px 8px 0}.chip em{color:#ff5c28;font-style:normal}
.ct{font:12px/1.6 'JetBrains Mono',monospace;color:#6f6a5f;word-break:break-all;margin:14px 0}
.step{display:flex;gap:18px;padding:18px 0;border-bottom:1px solid #1f1f23}.step b{flex:0 0 40px;font:600 13px 'JetBrains Mono',monospace;color:#ff5c28;width:34px}
.step div{font-size:15px;color:#b9b3a5;line-height:1.5}.step strong{display:block;color:#eae4d6;font-size:17px;margin-bottom:3px;font-weight:500}
.qrwrap{text-align:center;padding:14px}
.log{font:12px/1.9 'JetBrains Mono',monospace;color:#8d887c}.log .r{color:#ff6b57}.log .g{color:#4ade80}
[data-testid="stImage"] img{border-radius:14px;box-shadow:0 0 0 10px #f2ece0,0 30px 80px rgba(255,92,40,.25)}
[role=tablist]{display:flex!important;align-items:center!important;gap:6px!important;border-bottom:1px solid #1f1f23!important;padding-bottom:14px!important}
[role=tablist]::before{content:'CIPHER·QR';margin-right:auto;font:600 15px 'JetBrains Mono',monospace;letter-spacing:.18em;color:#ff5c28}
button[role=tab]{border-radius:99px!important;padding:9px 18px!important;height:auto!important;background:transparent!important}
button[role=tab][aria-selected=true]{background:#ff5c28!important}
button[role=tab] p{font:500 13px 'JetBrains Mono',monospace!important;letter-spacing:.08em!important;color:#8d887c!important}
button[role=tab][aria-selected=true] p{color:#0a0a0c!important}
</style>""", unsafe_allow_html=True)

ss = st.session_state
ss.setdefault("log", [])
ss.setdefault("sealed", None)
ss.setdefault("opened", None)


def log(kind, text):
    ss.log.insert(0, (datetime.now().strftime("%H:%M:%S"), kind, text))
    ss.log = ss.log[:12]


t_seal, t_open, t_how = st.tabs(["SEAL", "OPEN", "HOW IT WORKS"])

# ---------------- SEAL ----------------
with t_seal:
    L, R = st.columns(2, gap="large")
    with L:
        st.markdown('<h1 class="hero">Seal a secret<br>inside a <i>QR</i>.</h1><p class="sub">Your message is encrypted with AES-256-GCM before it ever becomes a code. Without the key, the QR is noise.</p>', unsafe_allow_html=True)
        st.markdown('<div class="lbl">SECRET MESSAGE</div>', unsafe_allow_html=True)
        msg = st.text_area("msg", height=130, label_visibility="collapsed", placeholder="Type the message to protect…", key="seal_msg")
        st.markdown('<div class="lbl">SECRET KEY</div>', unsafe_allow_html=True)
        key = st.text_input("key", type="password", label_visibility="collapsed", placeholder="Choose a strong key", key="seal_key")
        st.markdown(f'<div class="meter"><i style="width:{int(strength(key)*100)}%"></i></div>', unsafe_allow_html=True)
        if st.button("ENCRYPT & GENERATE QR →", key="go_seal"):
            if not msg.strip() or not key:
                st.error("Enter both a message and a secret key.")
            else:
                try:
                    payload = encrypt(msg, key)
                    if len(payload) > 2300:
                        st.error("Message is too long for one QR code (max about 1,600 characters).")
                    else:
                        ss.sealed = {"payload": payload, "png": png_bytes(make_qr(payload)), "chars": len(msg)}
                        log("g", f"sealed {len(msg)} chars → {len(payload)} B payload")
                except Exception as e:
                    st.error(str(e))
    with R:
        s = ss.sealed
        if s:
            a = anatomy(s["payload"])
            with st.container(key="card_seal"):
                st.image(s["png"], width=300)
                st.markdown(f'<div style="height:22px"></div><span class="chip"><em>AES</em>-256-GCM</span><span class="chip"><em>PBKDF2</em> {ITERATIONS//1000}k</span><span class="chip">salt {a["salt"]}B</span><span class="chip">nonce {a["nonce"]}B</span><span class="chip">tag {a["tag"]}B</span>', unsafe_allow_html=True)
                st.markdown('<div class="lbl">PAYLOAD (click the copy icon)</div>', unsafe_allow_html=True)
                st.code(s["payload"], language=None, wrap_lines=True)
                st.download_button("⬇ DOWNLOAD PNG", s["png"], "cipher-qr.png", "image/png")
        else:
            st.markdown('<div class="card" style="min-height:420px;display:flex;align-items:center;justify-content:center;color:#6f6a5f;font:13px \'JetBrains Mono\',monospace;letter-spacing:.1em">YOUR QR APPEARS HERE</div>', unsafe_allow_html=True)

# ---------------- OPEN ----------------
with t_open:
    L, R = st.columns(2, gap="large")
    with L:
        st.markdown('<h1 class="hero">Open a <i>sealed</i><br>message.</h1><p class="sub">Upload or photograph the QR, enter the key. A wrong key or a tampered code is detected and rejected, never shown as garbage.</p>', unsafe_allow_html=True)
        st.markdown('<div class="lbl">QR CODE</div>', unsafe_allow_html=True)
        src = st.radio("src", ["Upload image", "Use camera", "Paste payload"], horizontal=True, label_visibility="collapsed")
        data, pasted = None, None
        if src == "Upload image":
            f = st.file_uploader("up", type=["png", "jpg", "jpeg", "webp", "bmp"], label_visibility="collapsed")
            data = f.getvalue() if f else None
        elif src == "Use camera":
            c = st.camera_input("cam", label_visibility="collapsed")
            data = c.getvalue() if c else None
        else:
            pasted = st.text_area("paste", height=100, label_visibility="collapsed", placeholder="QRSM1.…")
        st.markdown('<div class="lbl">SECRET KEY</div>', unsafe_allow_html=True)
        okey = st.text_input("okey", type="password", label_visibility="collapsed", placeholder="Enter the key", key="open_key")
        if st.button("SCAN & DECRYPT →", key="go_open"):
            ss.opened = None
            payload = pasted if src == "Paste payload" else (scan_qr(data) if data else None)
            if not payload:
                ss.opened = ("err", "No QR code found. Upload a clear image of the QR." if src != "Paste payload" else "Paste a payload first.")
            elif not okey:
                ss.opened = ("err", "Enter the secret key.")
            else:
                t0 = time.perf_counter()
                try:
                    text = decrypt(payload, okey)
                    ms = int((time.perf_counter() - t0) * 1000)
                    ss.opened = ("ok", text, ms)
                    log("g", "opened OK")
                except DecryptionError as e:
                    ss.opened = ("bad", str(e))
                    log("r", "rejected (authentication failed)")
    with R:
        o = ss.opened
        if o and o[0] == "ok":
            import html
            st.markdown(f'<div class="card ok"><div class="tag" style="color:#4ade80">● AUTHENTICATED · KEY CORRECT</div><div class="msg">{html.escape(o[1])}</div><span class="chip">GCM tag verified</span><span class="chip">decrypted in {o[2]} ms</span></div>', unsafe_allow_html=True)
        elif o and o[0] == "bad":
            st.markdown(f'<div class="card bad"><div class="tag" style="color:#ff6b57">● DECRYPTION REJECTED</div><div style="margin-top:12px;color:#c9a39c;line-height:1.6">{o[1]}</div></div>', unsafe_allow_html=True)
        elif o:
            st.markdown(f'<div class="card bad"><div class="tag" style="color:#ff6b57">● NOTHING TO DECRYPT</div><div style="margin-top:12px;color:#c9a39c;line-height:1.6">{o[1]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card" style="min-height:260px;display:flex;align-items:center;justify-content:center;color:#6f6a5f;font:13px \'JetBrains Mono\',monospace;letter-spacing:.1em">DECRYPTED MESSAGE APPEARS HERE</div>', unsafe_allow_html=True)

# ---------------- HOW ----------------
with t_how:
    L, R = st.columns(2, gap="large")
    with L:
        st.markdown(f"""<h1 class="hero">The QR carries it.<br><i>Encryption</i> protects it.</h1><p class="sub">A QR is only a container. Here is exactly what happens to your message.</p>
<div class="step"><b>01</b><div><strong>Key derivation</strong>PBKDF2-HMAC-SHA256, {ITERATIONS:,} rounds, random 16-byte salt turns your password into a 256-bit key.</div></div>
<div class="step"><b>02</b><div><strong>AES-256-GCM encryption</strong>Fresh 12-byte nonce per message. Produces ciphertext plus a 16-byte authentication tag.</div></div>
<div class="step"><b>03</b><div><strong>Payload packing</strong>Version, salt, nonce, ciphertext and tag are Base64URL packed into one string.</div></div>
<div class="step"><b>04</b><div><strong>QR generation and scanning</strong>Error-correction level M. The receiver scans with OpenCV, then decrypts with the same key.</div></div>""", unsafe_allow_html=True)
    with R:
      with st.container(key="card_how"):
        st.markdown('<div class="lbl">PAYLOAD ANATOMY</div><div style="font:14px/2 \'JetBrains Mono\',monospace"><span style="color:#8d887c">QRSM1</span> . <span style="color:#ff5c28">salt·16B</span> <span style="color:#ffb03c">nonce·12B</span> <span style="color:#7dd3fc">ciphertext·n</span> <span style="color:#4ade80">tag·16B</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="lbl" style="margin-top:22px">PROPERTIES</div><span class="chip">Wrong key → rejected</span><span class="chip">1 flipped bit → rejected</span><span class="chip">Same text twice → different QR</span><span class="chip">Key never stored</span>', unsafe_allow_html=True)
        rows = "".join(f'<div class="{k}">{t} &nbsp; {x}</div>' for t, k, x in ss.log) or "No activity yet in this session."
        st.markdown(f'<div class="lbl" style="margin-top:22px">SESSION LOG</div><div class="log">{rows}</div>', unsafe_allow_html=True)
