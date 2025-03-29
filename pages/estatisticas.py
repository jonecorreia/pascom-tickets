import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from app_config import CREDITO

st.set_page_config(page_title="📊 Estatísticas de Vendas", page_icon="📈", layout="centered")
st.title("📊 Estatísticas de Tickets")
st.markdown("---")

data_path = "data/tickets_control.json"

def carregar_tickets():
    if os.path.exists(data_path):
        with open(data_path, "r") as f:
            return json.load(f)
    return []

# Carregamento inicial
tickets = carregar_tickets()

if not tickets:
    st.warning("Nenhum dado encontrado.")
    st.stop()

# Lista geral por grupo
st.subheader("📦 Grupos de Tickets")
df_geracoes = pd.DataFrame([
    {
        "Código": g.get("codigo_geracao"),
        "Título": g.get("titulo"),
        "Descrição": g.get("descricao"),
        "Data": g.get("data_geracao"),
        "Total de Tickets": len(g.get("tickets", []))
    } for g in tickets
])
st.dataframe(df_geracoes, use_container_width=True)

# Seleção para análise detalhada
opcoes_exibicao = []
codigos_exibicao = []
for g in tickets:
    try:
        data_formatada = datetime.strptime(g['data_geracao'], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
        opcoes_exibicao.append(f"{g['codigo_geracao']} - {g['titulo']} ({data_formatada})")
        codigos_exibicao.append(g['codigo_geracao'])
    except (KeyError, ValueError):
        continue
idx = st.selectbox("Selecione um grupo para análise detalhada:", range(len(opcoes_exibicao)), format_func=lambda i: opcoes_exibicao[i] if i < len(opcoes_exibicao) else "")
grupo_sel = codigos_exibicao[idx] if idx < len(codigos_exibicao) else None


valor_unitario = st.number_input("Valor por ticket (R$)", min_value=0.0, value=5.0, step=0.5)

# Filtragem
grupo = next((g for g in tickets if g.get("codigo_geracao") == grupo_sel), None)

if grupo:
    vendidos = 0
    datas = []
    for ticket in grupo["tickets"]:
        for h in ticket.get("historico", []):
            if h.get("status") in ["DISPONÍVEL", "REVENDA"]:
                vendidos += 1
                datas.append(datetime.strptime(h["data"], "%d/%m/%Y %H:%M:%S"))

    st.markdown(f"### 🎟️ Total vendido: `{vendidos}` de {len(grupo['tickets'])} tickets")
    st.markdown(f"### 💰 Total arrecadado: `R$ {vendidos * valor_unitario:.2f}`")

    # Gráfico de vendas por dia (plotly + Dash)
    vendas_por_dia = {}
    for ticket in grupo["tickets"]:
        for h in ticket.get("historico", []):
            if h.get("status") in ["DISPONÍVEL", "REVENDA"]:
                try:
                    data = datetime.strptime(h["data"], "%d/%m/%Y %H:%M:%S")
                    dia = data.strftime("%d/%m/%Y")
                    vendas_por_dia[dia] = vendas_por_dia.get(dia, 0) + 1
                except:
                    continue

    if vendas_por_dia:
        df_vendas = pd.DataFrame(list(vendas_por_dia.items()), columns=["dia", "Vendas"])
        fig = px.bar(df_vendas, x="dia", y="Vendas", labels={"dia": "Data", "Vendas": "Tickets Vendidos"}, title="Vendas por dia")
        st.plotly_chart(fig, use_container_width=True)

# Estatísticas complementares
if grupo:
    st.subheader("📈 Estatísticas detalhadas")

    df_historico = []
    for ticket in grupo["tickets"]:
        codigo = ticket["code"]
        for h in ticket.get("historico", []):
            df_historico.append({
                "code": codigo,
                "data": h.get("data"),
                "status": h.get("status")
            })

    if df_historico:
        df_h = pd.DataFrame(df_historico)
        df_h["data_dt"] = pd.to_datetime(df_h["data"], format="%d/%m/%Y %H:%M:%S")

        # Média de tickets por dia
        media_dia = df_h.groupby(df_h["data_dt"].dt.date).size().mean()
        st.markdown(f"- 📈 **Média de tickets vendidos por dia**: `{media_dia:.2f}`")

        # Horário de pico
        horario_pico = df_h["data_dt"].dt.hour.mode()[0]
        st.markdown(f"- 🕒 **Horário de pico das vendas**: `{horario_pico}h`")

        # Proporção entre DISPONÍVEL e REVENDA
        proporcoes = df_h["status"].value_counts(normalize=True) * 100
        st.markdown("- 📊 **Proporção entre status:**")
        for status, prop in proporcoes.items():
            st.markdown(f"    - `{status}`: `{prop:.1f}%`")

        # Tickets revendidos
        revendidos = df_h["code"].value_counts()
        num_revendidos = (revendidos > 1).sum()
        st.markdown(f"- 🔁 **Tickets revendidos**: `{num_revendidos}`")

        # Tempo médio entre primeira e última venda por ticket
        tempo_medio = []
        for code, grupo_ticket in df_h.groupby("code"):
            if len(grupo_ticket) > 1:
                delta = grupo_ticket["data_dt"].max() - grupo_ticket["data_dt"].min()
                tempo_medio.append(delta.total_seconds() / 3600)  # em horas
        if tempo_medio:
            media_horas = sum(tempo_medio) / len(tempo_medio)
            st.markdown(f"- ⏳ **Tempo médio entre revendas**: `{media_horas:.1f} horas`")

st.markdown("---")
st.caption(CREDITO)
