import streamlit as st
from camera_input_live import camera_input_live
import cv2
import numpy as np
import os
import json
from datetime import datetime
from app_config import CREDITO, STATUS_CORES
import base64
import time

# Configuração inicial
data_path = "data/tickets_control.json"

# Carregar tickets
def carregar_tickets():
    if os.path.exists(data_path):
        with open(data_path, "r") as file:
            return json.load(file)
    return []

# Atualizar tickets
def atualizar_tickets(tickets):
    with open(data_path, "w") as file:
        json.dump(tickets, file, indent=4)

# Verificar e marcar leitura
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

    # Ticket não localizado
    return False, data, leitura_atual['data'], leitura_atual['status']

# Interface Streamlit
st.set_page_config(page_title="Vendas", page_icon="🛒", layout="centered")
st.title("🛒 Vendas com QR-Code")
st.markdown("---")

# Controle de leitura
if "captura_ativa" not in st.session_state:
    st.session_state.captura_ativa = True

if "ultima_leitura" not in st.session_state:
    st.session_state.ultima_leitura = None

if "imagem_leitura" not in st.session_state:
    st.session_state.imagem_leitura = None

if "audio" not in st.session_state:
    st.session_state.audio = False

btn = st.button(
    "PARAR LEITURAS" if st.session_state.captura_ativa else "INICIAR LEITURAS",
    use_container_width=True
)

if btn:
    st.session_state.captura_ativa = not st.session_state.captura_ativa

st.markdown(f"<small>Leituras {'ativas' if st.session_state.captura_ativa else 'pausadas'}</small>", unsafe_allow_html=True)

# Captura da câmera
if st.session_state.captura_ativa:
    image = camera_input_live()
else:
    image = None

if image is not None:
    bytes_data = image.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(cv2_img)

    if data and (st.session_state.ultima_leitura != data):
        st.session_state.ultima_leitura = data
        st.session_state.imagem_leitura = image

        localizado, codigo, data_venda, status = verificar_qrcode(data)
        cor = STATUS_CORES.get(status, "gray")

        st.toast(f"{status}: {codigo}", icon="✅")

        if status == "DISPONÍVEL":
            st.session_state.audio = True
        elif status == "REVENDA":
            st.session_state.audio = True
        elif status == "NÃO LOCALIZADO":
            st.session_state.audio = False

if st.session_state.audio:
    st.markdown("""
        <audio autoplay>
            <source src="https://actions.google.com/sounds/v1/cartoon/clang_and_wobble.ogg" type="audio/ogg">
        </audio>
    """, unsafe_allow_html=True)
    st.session_state.audio = False

# Mostrar imagem do QR lido
if st.session_state.imagem_leitura:
    st.image(st.session_state.imagem_leitura, caption="Última Leitura", width=300)

# Histórico de leituras
st.markdown("---")
st.subheader("Histórico de Leitura de Tickets")
placeholder = st.empty()

ultimas_leituras = []
tickets = carregar_tickets()
for geracao in tickets:
    for ticket in geracao['tickets']:
        if "historico" in ticket:
            for leitura in ticket['historico']:
                ultimas_leituras.append({
                    "code": ticket['code'],
                    "data": leitura['data'],
                    "status": leitura['status']
                })

ultimas_leituras.sort(key=lambda x: datetime.strptime(x['data'], "%d/%m/%Y %H:%M:%S"), reverse=True)

with placeholder.container():
    if ultimas_leituras:
        for leitura in ultimas_leituras[:10]:
            cor = STATUS_CORES.get(leitura['status'], "gray")
            st.markdown(
                f"🎟️ Código: {leitura['code']} | 📅 {leitura['data']} | <span style='color:{cor}; font-weight:bold'>{leitura['status']}</span>",
                unsafe_allow_html=True
            )
    else:
        st.info("Nenhuma leitura realizada até o momento.")

st.markdown("---")
st.caption(CREDITO)
