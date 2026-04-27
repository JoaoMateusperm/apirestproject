import streamlit as st
import pandas as pd
from datetime import timedelta, date, datetime

st.set_page_config(page_title="Dashboard de vendas", layout="wide")

st.title("Painel de Vendas Mensal")

#leitura arquivo
mes_atual = datetime.now().month
ano_atual = datetime.now().year
nome_arquivo = f"vendas_{mes_atual}{ano_atual}.parquet"

@st.cache_data
def carregar_dados(caminho):
    try:
        return pd.read_parquet(caminho)
    except FileNotFoundError:
        st.error(f"Arquivo {caminho} não encontrado. Rode a carga primeiro!")
        return pd.DataFrame()

df = carregar_dados(nome_arquivo)

if not df.empty:
    #datetime
    df['data'] = pd.to_datetime(df['data'])

    #filtros
    st.sidebar.header("Filtros")
    
    #filtro loja
    lojas = ['Todas'] + sorted(df['cod_empresa'].unique().tolist())
    loja_selecionada = st.sidebar.selectbox("Selecione a Loja", lojas)

    #filtro data
    min_data = df['data'].min().date()
    max_data = df['data'].max().date()
    periodo = st.sidebar.date_input("Selecione o Período", [min_data, max_data])

    #filtros DF
    df_filtrado = df.copy()
    if loja_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['cod_empresa'] == loja_selecionada]
    
    if len(periodo) == 2:
        df_filtrado = df_filtrado[
            (df_filtrado['data'].dt.date >= periodo[0]) & 
            (df_filtrado['data'].dt.date <= periodo[1])
        ]

    #exibição
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Vendas por Loja")
        tabela_loja = df_filtrado.groupby('cod_empresa')['venda_liquida'].sum().reset_index()
        st.dataframe(tabela_loja.style.format({'venda_liquida': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

    with col2:
        st.subheader("Top 10 Maiores Vendas")
        # maiores valores individuais de venda_liquida
        top_10 = df_filtrado.nlargest(10, 'venda_liquida')[['cod_empresa', 'venda_liquida']].reset_index(drop=True)
        st.dataframe(top_10, use_container_width=True, hide_index=True)
else:
    st.info("Aguardando carregamento de dados...")