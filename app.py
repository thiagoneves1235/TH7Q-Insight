from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from industrial_ai.analysis import analyze_dataframe, load_spreadsheet
from industrial_ai.sample_data import create_sample_data


st.set_page_config(page_title="Industrial Sheet AI", page_icon="🏭", layout="wide")
st.title("🏭 Industrial Sheet AI")
st.caption("Analise explicavel de planilhas industriais com Python e IA.")

with st.sidebar:
    st.header("Entrada de dados")
    uploaded_file = st.file_uploader("Envie CSV, XLSX ou XLS", type=["csv", "xlsx", "xls"])
    if uploaded_file is not None:
        data_source = st.radio("Fonte dos dados", ["Arquivo enviado", "Demonstracao"])
    else:
        data_source = "Demonstracao"

try:
    if uploaded_file is not None and data_source == "Arquivo enviado":
        dataframe = load_spreadsheet(uploaded_file)
    else:
        dataframe = create_sample_data()
    result = analyze_dataframe(dataframe)
except (ImportError, ValueError, OSError) as error:
    st.error(str(error))
    st.stop()

st.success(f"{len(result.data):,} linhas prontas para analise.".replace(",", "."))
metric_items = list(result.kpis.items())
for start in range(0, len(metric_items), 4):
    metric_columns = st.columns(4)
    for column, (label, value) in zip(metric_columns, metric_items[start:start + 4]):
        display = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        column.metric(label, display)

st.subheader("Insights automáticos")
for insight in result.insights:
    st.write(f"- {insight}")

left, right = st.columns(2)
with left:
    st.subheader("Distribuição dos dados")
    if result.numeric_columns:
        selected = st.selectbox("Coluna", result.numeric_columns)
        st.plotly_chart(px.histogram(result.data, x=selected), use_container_width=True)
    else:
        st.info("Nenhuma coluna numerica encontrada.")
with right:
    st.subheader("Sinalizações")
    if result.anomalies.empty:
        st.info("Nenhuma linha sinalizada.")
    else:
        st.dataframe(result.anomalies, use_container_width=True)

st.subheader("Dados carregados")
st.dataframe(result.data, use_container_width=True, height=320)
