import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import av
import cv2
import numpy as np
import os
import json
from datetime import datetime
import time
from app_config import CREDITO

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

# Verificar e marcar venda
def verificar_qrcode(data):
    tickets = carregar_tickets()
    for geracao in tickets:
        for ticket in geracao['tickets']:
            if ticket['code'] == data:
                venda_atual = {"data_venda": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
                if "vendas" not in ticket:
                    ticket['vendas'] = [venda_atual]
                    atualizar_tickets(tickets)
                    return True, venda_atual["data_venda"], 1
                else:
                    ticket['vendas'].append(venda_atual)
                    atualizar_tickets(tickets)
                    return False, venda_atual["data_venda"], len(ticket['vendas'])
    return None, None, 0

# Classe de processamento de vídeo
class QRCodeProcessor(VideoProcessorBase):
    def __init__(self):
        self.qr_detector = cv2.QRCodeDetector()
        self.last_detected = None
        self.message_time = None
        self.message_text = ""
        self.message_color = (0, 255, 0)

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")

        data, bbox, _ = self.qr_detector.detectAndDecode(img)
        if bbox is not None and data:
            if data != self.last_detected and data.startswith("P."):
                venda_status, data_venda, qtd_vendas = verificar_qrcode(data)

                if venda_status is True:
                    self.message_text = f"Ticket {data} vendido!"
                    self.message_color = (0, 255, 0)  # Verde
                    st.audio("https://actions.google.com/sounds/v1/cartoon/clang_and_wobble.ogg")
                elif venda_status is False:
                    self.message_text = f"Ticket {data} já vendido antes! ({qtd_vendas}x)"
                    self.message_color = (0, 0, 255)  # Vermelho
                else:
                    self.message_text = "Ticket não encontrado!"
                    self.message_color = (0, 0, 255)  # Vermelho

                self.message_time = datetime.now()
                self.last_detected = data

            n_points = len(bbox)
            for j in range(n_points):
                pt1 = tuple(bbox[j][0].astype(int))
                pt2 = tuple(bbox[(j + 1) % n_points][0].astype(int))
                cv2.line(img, pt1, pt2, color=(0, 255, 0), thickness=2)

        if self.message_time and (datetime.now() - self.message_time).seconds < 3:
            cv2.putText(img, self.message_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, self.message_color, 2, cv2.LINE_AA)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# Interface Streamlit
st.set_page_config(page_title="Vendas", page_icon="🛒", layout="centered")
st.title("🛒 Vendas com QR-Code")
st.markdown("---")

webrtc_streamer(
    key="qr-code-scanner",
    video_processor_factory=QRCodeProcessor,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
)

st.markdown("---")
st.subheader("Últimas Vendas")
placeholder = st.empty()

while True:
    tickets = carregar_tickets()
    ultimas_vendas = []

    for geracao in tickets:
        for ticket in geracao['tickets']:
            if "vendas" in ticket:
                for idx, venda in enumerate(ticket["vendas"]):
                    ultimas_vendas.append({"code": ticket['code'], "data_venda": venda["data_venda"], "primeira_venda": idx == 0})

    ultimas_vendas.sort(key=lambda x: datetime.strptime(x['data_venda'], "%d/%m/%Y %H:%M:%S"), reverse=True)

    with placeholder.container():
        if ultimas_vendas:
            for venda in ultimas_vendas[:10]:
                cor_texto = "green" if venda['primeira_venda'] else "red"
                st.markdown(f"<span style='color:{cor_texto}'>🎟️ Código: {venda['code']} | 📅 Vendido em: {venda['data_venda']}</span>", unsafe_allow_html=True)
        else:
            st.info("Nenhum ticket vendido até o momento.")

    time.sleep(3)
