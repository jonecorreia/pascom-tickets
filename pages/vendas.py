import streamlit as st
from camera_input_live import camera_input_live
import cv2
import numpy as np
import os
import json
from datetime import datetime
from app_config import CREDITO, STATUS_CORES
from PIL import Image, ImageDraw
import io

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

    return False, data, leitura_atual['data'], leitura_atual['status']

# Interface Streamlit
st.set_page_config(page_title="Vendas", page_icon="🛒", layout="centered")
st.title("🛒 Vendas com QR-Code")
st.markdown("---")

if "captura_ativa" not in st.session_state:
    st.session_state.captura_ativa = True

if "ultima_leitura" not in st.session_state:
    st.session_state.ultima_leitura = None

if "imagem_leitura" not in st.session_state:
    st.session_state.imagem_leitura = None

if "audio" not in st.session_state:
    st.session_state.audio = False

if "usar_audio" not in st.session_state:
    st.session_state.usar_audio = True

if "bbox_leitura" not in st.session_state:
    st.session_state.bbox_leitura = None

col_btn, col_cb, col_play = st.columns([4, 1, 1])

with col_btn:
    texto_botao = "🔴 PARAR LEITURAS" if st.session_state.captura_ativa else "🟢 INICIAR LEITURAS"
    if st.button(texto_botao, use_container_width=True):
        st.session_state.captura_ativa = not st.session_state.captura_ativa

with col_cb:
    st.session_state.usar_audio = st.checkbox("Som", value=st.session_state.usar_audio)

with col_play:
    if st.button("▶️", help="Testar som"):
        st.markdown("""
        <script>
        var audio = document.getElementById("beep-audio");
        if(audio) { audio.play(); }
        </script>
        """, unsafe_allow_html=True)

st.markdown(f"<p style='color:gray'>Leituras {'ativas' if st.session_state.captura_ativa else 'pausadas'}</p>", unsafe_allow_html=True)

# Pré-carregar o som de venda (invisível, preparado para execução)
st.markdown("""
<audio id="beep-audio" preload="auto">
    <source src="https://actions.google.com/sounds/v1/cartoon/magic_chime.ogg" type="audio/mpeg">
</audio>
""", unsafe_allow_html=True)

# Detectar se está em dispositivo móvel
user_agent = st.session_state.get("_browser_user_agent", "")
usar_camera_traseira = "Mobile" in user_agent or "Android" in user_agent or "iPhone" in user_agent

# Captura da câmera (sem device_index, apenas controle de ativação)
image = camera_input_live() if st.session_state.captura_ativa else None

# Layout da visualização com colunas
st.markdown("## 📷 Visualização")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🎥 Câmera ao vivo")
    if image is not None:
        st.image(image, caption="Preview", use_container_width=True)

with col2:
    st.markdown("#### ✅ Última leitura")
    if st.session_state.imagem_leitura:
        pil_image = Image.open(st.session_state.imagem_leitura)
        draw = ImageDraw.Draw(pil_image)

        if st.session_state.bbox_leitura is not None:
            bbox = st.session_state.bbox_leitura.astype(int)
            for i in range(len(bbox[0])):
                pt1 = tuple(bbox[0][i])
                pt2 = tuple(bbox[0][(i + 1) % len(bbox[0])])
                draw.line([pt1, pt2], fill="green", width=5)

        st.image(pil_image, caption="Última Leitura", use_container_width=True)

# Processamento da imagem
if image is not None:
    bytes_data = image.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(cv2_img)

    if data and (st.session_state.ultima_leitura != data):
        st.session_state.ultima_leitura = data
        st.session_state.imagem_leitura = image
        st.session_state.bbox_leitura = bbox

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
