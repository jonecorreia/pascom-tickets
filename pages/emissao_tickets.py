import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import white
from PIL import Image
import qrcode
import io
import os
import json
from config import *
from datetime import datetime
import uuid

# Configuração inicial da página
st.set_page_config(page_title="Emissão de Tickets", page_icon="🏷️", layout="centered")

st.title("🏷️ EMISSÃO DE TICKETS")
st.markdown("---")

# Campos adicionais
pdf_titulo = st.text_input("Título", value="")
pdf_descricao = st.text_area("Descrição", value="")

# Carregar imagem inicial dos tickets
uploaded_file = st.file_uploader("Faça upload da imagem dos tickets em branco", type=["png", "jpg", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Imagem carregada", use_column_width=True)

    num_tickets = st.number_input("Número de tickets a gerar", min_value=1, max_value=1000, value=36)

    st.markdown("### Configuração da página")
    cols = st.number_input("Número de colunas", min_value=1, max_value=10, value=3)
    rows = st.number_input("Número de linhas", min_value=1, max_value=15, value=8)

    ticket_width_mm = st.number_input("Largura do ticket (mm)", min_value=10, max_value=100, value=60)
    ticket_height_mm = st.number_input("Altura do ticket (mm)", min_value=10, max_value=100, value=33)

    ticket_text = st.text_input("Texto do ticket (Ex.: MINGAU, TAPIOCA)", value="")
    page_break = st.number_input("Quebra automática de página após quantos tickets", min_value=1, max_value=100, value=24)

    if uploaded_file and st.button("Gerar Tickets"):
        if not os.path.exists("data"):
            os.makedirs("data")

        pdf_number = len(os.listdir("data")) + 1
        pdf_filename = f"P.{pdf_number:05d}.pdf"
        pdf_path = os.path.join("data", pdf_filename)

        # Gerar identificador único para controle interno
        codigo_geracao = str(uuid.uuid4())

        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4

        ticket_width = ticket_width_mm * 2.83465
        ticket_height = ticket_height_mm * 2.83465

        ticket_data = []
        current_ticket = 1
        ticket_counter = 0

        for page in range((num_tickets - 1) // (cols * rows) + 1):
            for row in range(rows):
                for col in range(cols):
                    if current_ticket > num_tickets:
                        break

                    if ticket_counter >= page_break:
                        c.showPage()
                        ticket_counter = 0

                    x = 50 + col * ticket_width
                    y = height - (50 + (row + 1) * ticket_height)

                    code = f"P.{pdf_number:05d}.{current_ticket:05d}"

                    qr = qrcode.make(code)
                    qr_pil = qr.get_image()

                    c.drawInlineImage(img, x, y, width=ticket_width, height=ticket_height)
                    c.drawInlineImage(qr_pil, x + ticket_width - 60, y + ticket_height - 60, width=50, height=50)

                    c.setFont("Helvetica-Bold", 6)
                    c.drawString(x + 5, y + 3, code)

                    c.setFillColor(white)
                    c.setFont("Helvetica-Bold", 10)
                    c.drawRightString(x + ticket_width - 5, y + 10, ticket_text)
                    c.setFillColor("black")

                    ticket_data.append({"pdf": pdf_filename, "ticket_number": current_ticket, "code": code, "description": ticket_text})                    

                    current_ticket += 1
                    ticket_counter += 1

            c.showPage()
            ticket_counter = 0

        c.save()

        with open(pdf_path, "rb") as pdf_file:
            st.download_button("Baixar PDF", pdf_file, file_name=pdf_filename)

        st.session_state['ticket_data'] = ticket_data
        st.session_state['pdf_filename'] = pdf_filename
        st.session_state['pdf_titulo'] = pdf_titulo
        st.session_state['pdf_descricao'] = pdf_descricao
        st.session_state['gerado_em'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state['validado'] = False
        st.session_state['codigo_geracao'] = codigo_geracao

    if "ticket_data" in st.session_state and st.button("VALIDAR"):
        persist_path = "data/tickets_control.json"

        if os.path.exists(persist_path):
            with open(persist_path, "r") as file:
                stored_data = json.load(file)
        else:
            stored_data = []

        stored_data.append({
            "codigo_geracao": st.session_state['codigo_geracao'],
            "titulo": st.session_state['pdf_titulo'],
            "descricao": st.session_state['pdf_descricao'],
            "pdf": st.session_state['pdf_filename'],
            "data_geracao": st.session_state['gerado_em'],
            "validado": True,
            "tickets": st.session_state['ticket_data']
        })

        with open(persist_path, "w") as file:
            json.dump(stored_data, file, indent=4)

        st.success("Tickets validados e armazenados com sucesso!")

st.markdown("---")
st.caption(CREDITO)
