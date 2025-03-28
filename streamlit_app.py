import streamlit as st

# Configuração inicial da página
st.set_page_config(page_title="Controle de Tickets", page_icon="🎟️", layout="centered")

# Cabeçalho simples
st.title("🎟️ PASCOM - Sistema de Tickets")

st.markdown("---")

# Opções do Menu (apenas duas implementadas no momento)
menu_options = ["🏷️ EMISSÃO DE TICKETS", "🛒 VENDAS"]

# Exibição das opções como botões grandes
col1, col2 = st.columns(2)

with col1:
    if st.button(menu_options[0], use_container_width=True):
        st.switch_page("emissao_tickets.py")

with col2:
    if st.button(menu_options[1], use_container_width=True):
        st.switch_page("vendas.py")

st.markdown("---")

# Rodapé simples
st.caption("Desenvolvido por Jone Correia")