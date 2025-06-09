import streamlit as st
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import datetime
from .db import conexaoBD, ResetarBD, DeletarBD
from .queries import BuscarGruposArmados, BuscarLideresPoliticos, BuscarDivisoes, BuscarPaises, BuscarConflitos
from .plots import gerarHistograma
from .inserts import (
    InserirGrupoArmado,
    InserirParticipacaoConflito,
    InserirLiderPolitico,
    InserirDivisaoMilitar,
    InserirChefeMilitar,
    InserirConflitoBelico
)

# Documentação da biblioteca de interface streamlit
# https://docs.streamlit.io/

def main(TipoConexao):
    st.set_page_config(
        page_title="Conflitos BélicosBD",
        page_icon="⚔️",
        layout="wide",
    )
    st.title("⚔️ Conflitos BélicosBD")

    # Botão de Reset
    if st.button("Resetar Banco de Dados", type="primary"):
        with st.spinner("Resetando o banco de dados..."):
            ResetarBD(TipoConexao)

    # Botão de Delete
    if st.button("Deletar tuplas do Banco de Dados", type="primary"):
        with st.spinner("Deletando as tuplas do banco de dados..."):
            DeletarBD(TipoConexao)
    
    tabInsercoes, tabConsultas = st.tabs(["📝 Inserções", "📊 Consultas"])

    with tabInsercoes:
        st.header("Inserções de Novos Dados")
        opcoesInsercao = [
            "Grupo Armado", "Participação em Conflito", "Líder Político",
            "Divisão Militar", "Chefe Militar", "Conflito Bélico",
        ]
        escolha = st.segmented_control(
            "Selecione o tipo de dados para inserir:",
            opcoesInsercao
        )

        # Obter conexão usando o TipoConexao
        conn = conexaoBD(TipoConexao) 
        if not conn:
            st.error(f"Falha ao estabelecer conexão com o banco de dados {TipoConexao.upper()}.")
        else:
            try:
                if escolha == "Grupo Armado":
                    InserirGrupoArmado(conn)
                elif escolha == "Participação em Conflito":
                    InserirParticipacaoConflito(conn)
                elif escolha == "Líder Político":
                    InserirLiderPolitico(conn)
                elif escolha == "Divisão Militar":
                    InserirDivisaoMilitar(conn)
                elif escolha == "Chefe Militar":
                    InserirChefeMilitar(conn)
                elif escolha == "Conflito Bélico":
                    InserirConflitoBelico(conn)
            finally:
                if conn: 
                    conn.close()

    with tabConsultas:
        st.header("📊 Consultas no Banco de Dados")
        st.subheader("Histograma de Tipos de Conflito")
        st.write("Visualize a distribuição dos conflitos por tipo")

        if st.button("Gerar Histograma", type="primary"):
            with st.spinner("Gerando Histograma..."):
                gerarHistograma(TipoConexao) # Passa o tipo de conexão
