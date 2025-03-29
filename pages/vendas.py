import streamlit as st
import os
import json
from datetime import datetime
from config import CREDITO
from PIL import Image
from pyzbar.pyzbar import decode

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

# Interface da câmera via Streamlit (web)
enable = st.checkbox("📸 Ativar câmera")
picture = st.camera_input("Tirar foto do QR-Code", disabled=not enable)

if picture:
    image = Image.open(picture)
    decoded_data = decode(image)

    if decoded_data:
        qr_code = decoded_data[0].data.decode('utf-8')

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
        st.error("Nenhum QR-Code detectado na imagem.")

st.markdown("---")

# Exibir últimas vendas
st.subheader("Últimas Vendas")
tickets = carregar_tickets()
ultimas_vendas = []

for geracao in tickets:
    for ticket in geracao['tickets']:
        if "vendido" in ticket:
            ultimas_vendas.append(ticket)

ultimas_vendas.sort(key=lambda x: datetime.strptime(x['data_venda'], "%d/%m/%Y %H:%M:%S"), reverse=True)

if ultimas_vendas:
    for venda in ultimas_vendas[:10]:
        st.write(f"🎟️ Código: {venda['code']} | 📅 Vendido em: {venda['data_venda']}")
else:
    st.info("Nenhum ticket vendido até o momento.")

st.markdown("---")
st.caption(CREDITO)
