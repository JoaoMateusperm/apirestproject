import pandas as pd
import psycopg2 as pg
import os
import logging
import argparse
import streamlit as st
from datetime import timedelta, date, datetime
from calendar import monthrange
from dotenv import load_dotenv

#Config log
logging.basicConfig(level=logging.INFO)

#conectar com DB
load_dotenv()

DATABASE = os.getenv("DB_NAME")
HOST = os.getenv("DB_HOST")
USERSERVER = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASS")
PORT = os.getenv("DB_PORT")

conn_dw = pg.connect(database=DATABASE, host=HOST, user=USERSERVER, password=PASSWORD, port=PORT)
cur = conn_dw.cursor()

#data inicial e final do mês:
def executar_carga():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mes", type=int, required=False)
    parser.add_argument("--ano", type=int, required=False)
    parser.add_argument("--data_final", type=str, required=False)
    args = parser.parse_args()
    
    hoje = datetime.now()

    if args.mes and args.ano:
        mes = args.mes
        ano = args.ano
    else:
        data_ref = hoje - timedelta(days=1)
        mes = data_ref.month
        ano = data_ref.year

    data_inicial = date(ano, mes, 1)

    if args.data_final:
        data_final = datetime.strptime(args.data_final, "%Y-%m-%d")
    else:
        if mes == hoje.month and ano == hoje.year:
            data_final = hoje - timedelta(days=1)
        else:
            ultimo_dia = monthrange(ano, mes)[1]
            data_final = datetime(ano, mes, ultimo_dia)

    logging.info(f"Período da carga: {data_inicial} até {data_final}")

    #query extração
    query = f""" 
SELECT cod_empresa, data, venda_liquida FROM fat_vendas 
WHERE data 
BETWEEN '{data_inicial}' AND '{data_final}'
"""
    df = pd.read_sql(query, conn_dw)

    conn_dw.close()

    if not df.empty:
        #gerar nome arquivo
        nome_arquivo = f"vendas_{mes}{ano}.parquet"
        df.to_parquet(nome_arquivo, index=False)
        logging.info(f"Arquivo {nome_arquivo} gerado com sucesso!")
    else:
        logging.warning("Nenhum dado encontrado para o período.")



