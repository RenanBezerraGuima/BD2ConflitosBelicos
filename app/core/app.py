import streamlit as st
from .db import conexaoBD, ResetarBD, DeletarBD
from .plots import (
	gerarHistograma,
    listarII,
    listarIII,
    listarIV,
    listarV,
    listarVI,
)
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

        # i. Histograma
        st.subheader("Histograma de Tipos de Conflito")
        st.write("Visualize a distribuição dos conflitos por tipo")

        if st.button("Gerar Histograma", type="primary"):
            with st.spinner("Gerando Histograma..."):
                gerarHistograma(TipoConexao) # Passa o tipo de conexão
        
        st.divider()

        # ii. Fornecedores de Barret M82 / M200"
        st.subheader("ii. Fornecedores de Alta Periculosidade")
        st.write("Liste os fornecedores de armamentos do tipo Barret M82 ou M200 Intervention")
        if st.button("Listar"):
            listarII(TipoConexao)

        st.divider()

        # iii. 5 maiores conflitos
        st.subheader("iii. Maiores Conflitos")
        st.write("Liste os 5 conflitos com os maiores números de vítimas fatais")
        if st.button("Listar", key='listar_iii'):
            listarIII(TipoConexao)

        st.divider()

        # iv. 5 maiores organizações
        st.subheader("iv. Maiores Organizações")
        st.write("Liste as 5 maiores organizações baseado em número de mediações")
        if st.button("Listar", key='listar_iv'):
            listarIV(TipoConexao)

        st.divider()

        # v. 5 maiores grupos armados
        st.subheader("v. Maiores Grupos Armados")
        st.write("Liste os 5 maiores grupos armados baseado no número de armas fornecidas")
        if st.button("Listar", key='listar_v'):
            listarV(TipoConexao)

        st.divider()

        # vi. País com o maior número de conflitos religiosos
        st.subheader("vi. País Mais Afetado por Conflitos Religiosos")
        st.write("Liste o país mais envolvido em conflitos de natureza religiosa")
        if st.button("Listar", key='listar_vi'):
            listarVI(TipoConexao)

        st.divider()
