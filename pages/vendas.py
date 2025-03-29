import streamlit as st
import os
import json
from datetime import datetime
from config import CREDITO
import cv2
from pyzbar.pyzbar import decode
import numpy as np

# Configuração inicial
data_path = "data/tickets_control.json"

st.set_page_config(page_title="Vendas", page_icon="🛒", layout="centered")
st.title("🛒 Vendas")
st.markdown("---")

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

# Ler QR Code
def ler_qr_code():
    cap = cv2.VideoCapture(0)
    decoded_data = None

    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("Não foi possível acessar a câmera.")
            break

        for barcode in decode(frame):
            decoded_data = barcode.data.decode('utf-8')
            cap.release()
            cv2.destroyAllWindows()
            return decoded_data

        cv2.imshow("QR Code Scanner - Pressione 'q' para sair", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None

if st.button("📷 Ler QR-Code"):
    qr_code = ler_qr_code()

    if qr_code:
        tickets = carregar_tickets()
        ticket_encontrado = False

        for geracao in tickets:
            for ticket in geracao['tickets']:
                if ticket['code'] == qr_code:
                    ticket_encontrado = True
                    if "vendido" not in ticket:
                        ticket['vendido'] = True
                        ticket['data_venda'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        atualizar_tickets(tickets)
                        st.success(f"Ticket {qr_code} marcado como vendido.")
                    else:
                        st.warning(f"Ticket {qr_code} já foi vendido em {ticket['data_venda']}.")
                    break
            if ticket_encontrado:
                break

        if not ticket_encontrado:
            st.error("Ticket não encontrado.")
    else:
        st.warning("Nenhum QR-Code detectado.")

st.markdown("---")

# Exibir últimos tickets vendidos
st.subheader("Últimas Vendas")
tickets = carregar_tickets()
ultimas_vendas = []

for geracao in tickets:
    for ticket in geracao['tickets']:
        if "vendido" in ticket:
            ultimas_vendas.append(ticket)

ultimas_vendas.sort(key=lambda x: datetime.strptime(x['data_venda'], "%d/%m/%Y %H:%M:%S"), reverse=True)

if ultimas_vendas:
    for venda in ultimas_vendas[:10]:  # Exibir apenas as 10 últimas vendas
        st.write(f"🎟️ Código: {venda['code']} | 📅 Vendido em: {venda['data_venda']}")
else:
    st.info("Nenhum ticket vendido até o momento.")

st.markdown("---")
st.caption(CREDITO)
