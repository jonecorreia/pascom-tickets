import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.page_link("streamlit_app.py", label="Início", icon="🏠")
        st.page_link("pages/gerenciamento.py", label="Gerenciamento", icon="📁")
        st.page_link("pages/vendas.py", label="Vendas (PC)", icon="🛒")
        st.page_link("pages/vendas_mobile.py", label="Vendas Mobile", icon="📱")
        # adicione outros links conforme necessidade
