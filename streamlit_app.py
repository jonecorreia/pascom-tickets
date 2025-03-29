import streamlit as st
from config import *

# Configuração inicial da página
st.set_page_config(page_title="Controle de Tickets", page_icon="🎟️", layout="centered")

# Cabeçalho simples
st.title("🎟️ PASCOM - Sistema de Tickets")

st.markdown("---")

# Opções do Menu
menu_options = ["🏷️ EMISSÃO DE TICKETS", "🛒 VENDAS", "📊 ESTATÍSTICAS DE TICKETS", "⚙️ GERENCIAMENTO"]

# Exibição das opções como botões grandes
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    if st.button(menu_options[0], use_container_width=True):
        st.switch_page("pages/emissao_tickets.py")

with col2:
    if st.button(menu_options[1], use_container_width=True):
        st.switch_page("pages/vendas.py")

with col3:
    if st.button(menu_options[2], use_container_width=True):
        st.switch_page("pages/estatisticas.py")

with col4:
    if st.button(menu_options[3], use_container_width=True):
        st.switch_page("pages/gerenciamento.py")

# Rodapé simples
st.markdown("---")
st.caption(CREDITO)