import streamlit as st
import os
import qrcode
import uuid
import random
import requests
from io import BytesIO

# --- ESTILO Y DISEÑO ---
st.set_page_config(page_title="DropQR Elite", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #05070a; color: white; }
    .aura-container {
        position: relative; width: 220px; height: 220px;
        margin: 20px auto; display: flex; align-items: center; justify-content: center;
    }
    .aura-ring {
        position: absolute; width: 100%; height: 100%; border-radius: 50%;
        background: conic-gradient(from 0deg, #00d2ff, #3a7bd5, #00d2ff, #0052d4, #00d2ff);
        animation: rotate-aura 2s linear infinite; filter: blur(20px); opacity: 0.8;
    }
    .aura-inner {
        position: relative; width: 180px; height: 180px; background: #05070a;
        border-radius: 50%; display: flex; flex-direction: column;
        align-items: center; justify-content: center; z-index: 2;
        border: 2px solid rgba(0, 210, 255, 0.3);
    }
    @keyframes rotate-aura { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .pin-text {
        color: #00d2ff; font-size: 3rem; font-weight: 900; margin: 0;
        text-shadow: 0 0 15px rgba(0, 210, 255, 0.7); font-family: monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE CONEXIÓN ---
if 'session_id' not in st.session_state:
    query_id = st.query_params.get("id")
    st.session_state.session_id = query_id if query_id else str(uuid.uuid4())[:8]
    st.session_state.pin = str(random.randint(1000, 9999))
    st.session_state.is_pc = False if query_id else True
    st.session_state.auth = True if st.session_state.is_pc else False

# --- SONIDO ---
def play_sound():
    audio_html = """<audio autoplay><source src="data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YT1vT19vT19vT19v" type="audio/wav"></audio>"""
    st.markdown(audio_html, unsafe_allow_html=True)

# --- PANTALLA DE ACCESO (MÓVIL) ---
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🔐 VINCULAR</h1>", unsafe_allow_html=True)
    pin_input = st.text_input("Ingresa el PIN", type="password")
    if st.button("CONECTAR"):
        if pin_input == st.session_state.pin:
            play_sound()
            st.session_state.auth = True
            st.rerun()
        else: st.error("PIN Incorrecto")
    st.stop()

# --- PANEL PRINCIPAL ---
folder = f"data_{st.session_state.session_id}"
if not os.path.exists(folder): os.makedirs(folder)

col1, col2 = st.columns([1, 2])

with col1:
    if st.session_state.is_pc:
        st.markdown(f"""<div class="aura-container"><div class="aura-ring"></div><div class="aura-inner">
            <p style="color:#3a7bd5; font-size:0.7rem; margin:0;">PIN</p>
            <p class="pin-text">{st.session_state.pin}</p></div></div>""", unsafe_allow_html=True)
        url = f"https://tu-link.streamlit.app/?id={st.session_state.session_id}"
        qr = qrcode.make(url)
        buf = BytesIO()
        qr.save(buf)
        st.image(buf, use_container_width=True)
    else: st.success("📱 DISPOSITIVO VINCULADO")

with col2:
    st.subheader("📤 Transferencia (1GB)")
    files = st.file_uploader("Subir", accept_multiple_files=True, label_visibility="collapsed")
    if files:
        for f in files:
            with open(os.path.join(folder, f.name), "wb") as out: out.write(f.getbuffer())
        play_sound()
        st.toast("✅ Recibido")

    st.divider()
    for item in os.listdir(folder):
        with open(os.path.join(folder, item), "rb") as fb:
            st.download_button(f"📥 {item}", fb, file_name=item, use_container_width=True)

if st.sidebar.button("🗑️ Reset"):
    st.session_state.clear()
    st.rerun()
