import streamlit as st
import os
import json
from datetime import datetime
from app_config import *

# Página inicial
st.set_page_config(page_title="Gerenciamento de Tickets", page_icon="⚙️", layout="wide")
st.title("⚙️ Gerenciamento de Gerações")
st.markdown("---")

persist_path = "data/tickets_control.json"

# Carregar dados
if os.path.exists(persist_path):
    with open(persist_path, "r") as file:
        stored_data = json.load(file)
else:
    stored_data = []

# Ordenar dados pela data mais recente
stored_data.sort(key=lambda x: datetime.strptime(x['data_geracao'], "%Y-%m-%d %H:%M:%S"), reverse=True)

if stored_data:
    for idx, item in enumerate(stored_data):
        data_formatada = datetime.strptime(item['data_geracao'], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
        with st.expander(f"📄 {data_formatada} - {item['titulo']}", expanded=False):
            st.markdown(f"**🆔 Código de Geração:** {item['codigo_geracao']}")
            st.markdown(f"**🗓️ Data:** {data_formatada}")
            st.markdown(f"**📌 Título:** {item['titulo']}")
            st.markdown(f"**📝 Descrição:** {item['descricao']}")
            st.markdown(f"**✅ Validado:** {'Sim' if item['validado'] else 'Não'}")

            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                if st.button("🔍 Ver detalhes", key=f"details_{idx}"):
                    st.switch_page("pages/detalhes.py")  # Página a ser criada futuramente

            with col2:
                pdf_path = os.path.join("data", item['pdf'])
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as file:
                        st.download_button("⬇️ Baixar PDF", file, file_name=item['pdf'], key=f"download_{idx}")
                else:
                    st.warning("Arquivo não encontrado")

            with col3:
                if st.button("🗑️ Remover", key=f"remove_{idx}"):
                    st.session_state[f"confirm_{idx}"] = True

                if st.session_state.get(f"confirm_{idx}", False):
                    st.warning(f"⚠️ Tem certeza que deseja excluir '{item['titulo']}'? Essa ação não pode ser desfeita.")
                    col_conf1, col_conf2 = st.columns(2)
                    with col_conf1:
                        if st.button("✅ Confirmar exclusão", key=f"confirm_del_{idx}"):
                            if os.path.exists(pdf_path):
                                os.remove(pdf_path)
                            stored_data.pop(idx)
                            with open(persist_path, "w") as file:
                                json.dump(stored_data, file, indent=4)
                            st.success("Operação removida com sucesso")
                            st.session_state[f"confirm_{idx}"] = False
                            st.experimental_rerun()
                    with col_conf2:
                        if st.button("❌ Cancelar", key=f"cancel_del_{idx}"):
                            st.session_state[f"confirm_{idx}"] = False
                            st.experimental_rerun()
else:
    st.info("Nenhuma geração encontrada.")

st.markdown("---")
st.caption(CREDITO)
