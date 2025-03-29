import streamlit as st
import cv2
import numpy as np
import os
import json
from datetime import datetime
from PIL import Image
from camera_input_live import camera_input_live
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

if "found_qr" not in st.session_state:
    st.session_state.found_qr = False

if "qr_code_image" not in st.session_state:
    st.session_state.qr_code_image = None

if "usar_audio" not in st.session_state:
    st.session_state.usar_audio = True

st.session_state.usar_audio = st.checkbox("Som", value=st.session_state.usar_audio)

st.markdown("""
<audio id="beep-audio" preload="auto">
    <source src="https://actions.google.com/sounds/v1/cartoon/magic_chime.ogg" type="audio/mpeg">
</audio>
""", unsafe_allow_html=True)

if not st.session_state.found_qr:
    image = camera_input_live()
else:
    image = st.session_state.qr_code_image

if image is not None:
    st.image(image, caption="Visualização da Câmera", use_container_width=True)
    bytes_data = image.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    detector = cv2.QRCodeDetector()
    data, bbox, straight_qrcode = detector.detectAndDecode(cv2_img)

    if data:
        st.session_state.found_qr = True
        st.session_state.qr_code_image = image

        localizado, codigo, data_venda, status = verificar_qrcode(data)
        cor = STATUS_CORES.get(status, "gray")
        st.toast(f"{status}: {codigo}", icon="✅")

        if status in ["DISPONÍVEL", "REVENDA"] and st.session_state.usar_audio:
            st.markdown("""
            <script>
            var audio = document.getElementById("beep-audio");
            if(audio) { audio.play(); }
            </script>
            """, unsafe_allow_html=True)

        with st.expander("Detalhes da Leitura"):
            st.write("Código:", data)
            st.write("BBox:", bbox)
            st.write("Data:", data_venda)
            st.write("Status:", status)

st.markdown("---")
st.caption(CREDITO)