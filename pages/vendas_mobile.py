import streamlit as st
import av
import cv2
import json
import numpy as np
import os
from datetime import datetime
from PIL import ImageDraw
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from app_config import CREDITO, STATUS_CORES

st.set_page_config(page_title="📱 Vendas Mobile", page_icon="📱", layout="centered")

# Configuração inicial
data_path = "data/tickets_control.json"

# Carregar e atualizar tickets
def carregar_tickets():
    if os.path.exists(data_path):
        with open(data_path, "r") as file:
            return json.load(file)
    return []

def atualizar_tickets(tickets):
    with open(data_path, "w") as file:
        json.dump(tickets, file, indent=4)

# Verificação e marcação de leitura
def verificar_qrcode(data):
    tickets = carregar_tickets()
    leitura_atual = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "status": "NÃO LOCALIZADO"
    }
    for geracao in tickets:
        for ticket in geracao['tickets']:
            if ticket['code'] == data:
                if "historico" not in ticket:
                    ticket['historico'] = []
                if "STATUS" not in ticket:
                    ticket['STATUS'] = "DISPONÍVEL"

                status = "DISPONÍVEL" if len(ticket['historico']) == 0 else "REVENDA"
                ticket['STATUS'] = status
                leitura_atual['status'] = status
                ticket['historico'].append(leitura_atual)
                atualizar_tickets(tickets)
                return True, ticket['code'], leitura_atual['data'], status

    return False, data, leitura_atual['data'], leitura_atual['status']

# Interface principal
st.title("📱 Vendas no Celular")
st.markdown("---")

if "usar_audio" not in st.session_state:
    st.session_state.usar_audio = True

if "ultima_leitura" not in st.session_state:
    st.session_state.ultima_leitura = None

st.markdown("""
<audio id="beep-audio" preload="auto">
    <source src="https://actions.google.com/sounds/v1/cartoon/magic_chime.ogg" type="audio/mpeg">
</audio>
""", unsafe_allow_html=True)

col1, col2 = st.columns([8, 2])
with col1:
    st.markdown("### Leitura com Câmera ao Vivo")
with col2:
    st.session_state.usar_audio = st.checkbox("Som", value=st.session_state.usar_audio)

# Seletor de câmera
camera_mode = st.selectbox(
    "Escolher câmera",
    options=["user", "environment"],
    index=1,
    format_func=lambda x: "📷 Frontal" if x == "user" else "🎯 Traseira"
)

# Processador de vídeo com leitura de QRCode
class VideoProcessor(VideoTransformerBase):
    def __init__(self):
        self.last_code = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(img)

        if bbox is not None and len(bbox) > 0:
            for i in range(len(bbox[0])):
                pt1 = tuple(bbox[0][i])
                pt2 = tuple(bbox[0][(i + 1) % len(bbox[0])])
                cv2.line(img, pt1, pt2, (0, 255, 0), 3)

        if data and data != self.last_code:
            self.last_code = data
            localizado, codigo, data_venda, status = verificar_qrcode(data)
            st.toast(f"{status}: {codigo}", icon="✅")
            if status in ["DISPONÍVEL", "REVENDA"] and st.session_state.usar_audio:
                st.markdown("""
                <script>
                var audio = document.getElementById("beep-audio");
                if(audio) { audio.play(); }
                </script>
                """, unsafe_allow_html=True)

        return img

# Stream de vídeo via WebRTC
webrtc_streamer(
    key="vendas-mobile",
    video_processor_factory=VideoProcessor,
    media_stream_constraints={
        "video": {
            "width": {"ideal": 1280},
            "height": {"ideal": 720},
            "facingMode": {"ideal": camera_mode}  # alterado para suportar sugestão JS do post
        },
        "audio": False
    },
    async_processing=True
)

st.markdown("---")
st.caption(CREDITO)
