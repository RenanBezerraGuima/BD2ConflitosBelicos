import streamlit as st
import psycopg
import matplotlib.pyplot as plt

# Documentação do biblioteca psycopg (PsycoticPostGre)
# https://www.psycopg.org/psycopg3/docs/basic/usage.html

# Os campos da conexão dependem da
# conexão e do usuário do postgreSQL
def conexaoBD():
    conexao = psycopg.connect(
        """
        dbname=postgres
        user=postgres
        host=localhost
        password=123456
        """
    )
    return conexao

def gerarHistograma(cursor):
    cursor.execute(
                """
                SELECT TipoConf, COUNT(*) AS NumeroDeConflitos
                FROM Conflito
                GROUP BY TipoConf ORDER BY NumeroDeConflitos DESC
                """
            )
    dadosHistograma = cursor.fetchall()
    if dadosHistograma:
        tipos = [item[0] for item in dadosHistograma]
        contagens = [item[1] for item in dadosHistograma]
        fig, ax = plt.subplots()
        ax.bar(tipos, contagens)
        plt.xlabel("Tipo de Conflito")
        plt.ylabel("Número de Conflitos")
        st.pyplot(fig)
    else:
        st.error("Não há dados sobre conflitos para gerar este histograma!")

# Teste do psycopg
conexao = conexaoBD()
with conexao.cursor() as cursor:
    # cursor.execute("SELECT * FROM ConflitoPais")
    # st.header("Tabela conflitos")
    # st.table(cursor.fetchall())
    st.title("Conflitos BélicosBD")

    tabInsercoes, tabConsultas = st.tabs(["Inserções", "Consultas"])
    with tabInsercoes:
        st.header("Inserções de Novos Dados")
        opcoesInsercao = ["Grupo Militar", "Líder Político", "Divisão Militar", "Chefe Militar", "Conflito Bélico"]
        escolha = st.segmented_control("Escolha abaixo qual dado deseja inserir no banco de dados",opcoesInsercao, selection_mode="single")
        match escolha:
            case "Grupo Militar":

    with tabConsultas:
        st.header("Consultas no Banco de Dados")

        st.subheader("Histograma de Tipos de Conflito")
        if st.button("Gerar Histograma", type="primary"):
            gerarHistograma(cursor)
