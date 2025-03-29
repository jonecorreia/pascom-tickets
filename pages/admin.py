import streamlit as st
import os
import json
import shutil
from app_config import CREDITO

st.set_page_config(page_title="🔧 Administração", page_icon="🛠️", layout="centered")
st.title("🛠️ Painel Administrativo")
st.markdown("---")

data_path = "data/tickets_control.json"
pdfs_dir = "pdfs"  # ajuste conforme sua estrutura

# Carregar tickets
def carregar_tickets():
    if os.path.exists(data_path):
        with open(data_path, "r") as f:
            return json.load(f)
    return []

def atualizar_tickets(tickets):
    with open(data_path, "w") as f:
        json.dump(tickets, f, indent=4)

# 1. Deletar tickets e arquivos PDF
def deletar_arquivos_pdfs():
    if os.path.exists("data"):
        for file in os.listdir("data"):
            if file.endswith(".pdf"):
                os.remove(os.path.join("data", file))

def deletar_tudo():
    if os.path.exists(data_path):
        os.remove(data_path)
    deletar_arquivos_pdfs()
    os.makedirs(pdfs_dir, exist_ok=True)

# 2. Limpar status de tickets
def limpar_status(geracao=None):
    tickets = carregar_tickets()
    for g in tickets:
        if geracao is None or g["codigo"] == geracao:
            for ticket in g["tickets"]:
                ticket["STATUS"] = "DISPONÍVEL"
                ticket["historico"] = []
    atualizar_tickets(tickets)

# Seção: Deletar tudo
st.subheader("🗑️ Deletar Todos os Tickets e PDFs")
with st.expander("⚠️ Confirmar operação de exclusão total"):
    confirmar_delecao = st.radio("Tem certeza que deseja excluir todos os dados?", ["Não", "Sim"], index=0)
    if confirmar_delecao == "Sim" and st.button("Deletar tudo", type="primary"):
        deletar_tudo()
        st.success("Todos os tickets e PDFs foram removidos com sucesso.")
    
st.markdown("---")

# Seção: Limpar status
st.subheader("♻️ Limpar Status de Tickets")
todos_tickets = carregar_tickets()
codigos = [g["codigo"] for g in todos_tickets if "codigo" in g]

opcao = st.radio("Escolha a geração a ser limpa:", ["Todas"] + codigos, horizontal=True)

with st.expander("⚠️ Confirmar limpeza de status"):
    confirmar_limpeza = st.radio("Deseja realmente limpar os status da seleção?", ["Não", "Sim"], index=0)
    if confirmar_limpeza == "Sim" and st.button("Limpar Status"):
        if opcao == "Todas":
            limpar_status()
        else:
            limpar_status(opcao)
        st.success("Status limpos com sucesso.")
    
st.markdown("---")
st.caption(CREDITO)
