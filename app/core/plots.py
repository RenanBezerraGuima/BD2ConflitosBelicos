import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from .db import conexaoBD

def gerarHistograma(TipoConexao):
    conn = conexaoBD(TipoConexao)
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                        """
                        SELECT TipoConf, COUNT(*) AS NumeroDeConflitos
                        FROM Conflito
                        GROUP BY TipoConf
                        ORDER BY NumeroDeConflitos DESC
                        """
                    )
            dados = cursor.fetchall()

        if dados:
            tipos = [item[0] for item in dados]
            contagens = [item[1] for item in dados]

            fig, ax = plt.subplots(figsize=(10,6))
            bars = ax.bar(tipos, contagens, color=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"])

            for bar, count in zip(bars, contagens):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        str(count), ha='center', va='bottom')

            ax.set_xlabel("Tipo de Conflito", fontsize=12)
            ax.set_ylabel("Número de Conflitos", fontsize=12)
            ax.set_title("Distribuição de Conflitos por Tipo", fontsize=14)

            plt.tight_layout()
            st.caption("Obs: Abaixo do histograma estão os dados nos quais ele foi gerado")
            st.pyplot(fig)

            df = pd.DataFrame(dados, columns=["Tipos de Conflito", "Número de Conflitos"])
            st.dataframe(df, use_container_width=False)
        else:
            st.info("Não há dados sobre conflitos para gerar este histograma!")
    except Exception as e:
        st.error(f"Erro ao gerar histograma: {e}")
    finally:
        if conn:
            conn.close()


def listarII(tipoConexao):
    conn = conexaoBD(tipoConexao)
    if not conn:
        return
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT nometraf, nomearma, numarmas, nomegrupo
                FROM public.fornece
                NATURAL JOIN public.grupoarmado
                WHERE nomearma='Barret M82' OR nomearma='M200 Intervention'
                """
            )
            dados = cur.fetchall()

            df = pd.DataFrame(dados, columns=["Traficante", 'Arma', 'Quantidade', 'Grupo'])
            st.dataframe(df, use_container_width=False)
    except Exception as ex:
        st.error(f"Erro ao fazer listagem. ${ex}")
    finally:
        if conn:
            conn.close()

def listarIII(tipoConexao):
    conn = conexaoBD(tipoConexao)
    if not conn:
        return
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT nome, tipoconf, nummortos, numferidos
                FROM public.conflito
                ORDER BY nummortos DESC
                LIMIT 5
                """
            )
            dados = cur.fetchall()

            df = pd.DataFrame(dados, columns=["Conflito", 'Tipo', 'Mortos', 'Feridos'])
            st.dataframe(df, use_container_width=False)
    except Exception as ex:
        st.error(f"Erro ao fazer listagem. ${ex}")
    finally:
        if conn:
            conn.close()

def listarIV(tipoConexao):
    conn = conexaoBD(tipoConexao)
    if not conn:
        return
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT nomeorg, COUNT(*) AS mediacoes
                FROM entradmed
                NATURAL JOIN organizacaom
                GROUP BY nomeorg
                ORDER BY mediacoes DESC
                LIMIT 5
                """
            )
            dados = cur.fetchall()

            df = pd.DataFrame(dados, columns=["Organização", 'Número de Mediações'])
            st.dataframe(df, use_container_width=False)
    except Exception as ex:
        st.error(f"Erro ao fazer listagem. ${ex}")
    finally:
        if conn:
            conn.close()

def listarV(tipoConexao):
    conn = conexaoBD(tipoConexao)
    if not conn:
        return
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT nomegrupo, SUM(numarmas) as armas
                FROM fornece
                NATURAL JOIN grupoarmado
                GROUP BY nomegrupo
                ORDER BY armas DESC
                LIMIT 5
                """
            )
            dados = cur.fetchall()

            df = pd.DataFrame(dados, columns=["Grupo", 'Número de Armas Totais'])
            st.dataframe(df, use_container_width=False)
    except Exception as ex:
        st.error(f"Erro ao fazer listagem. ${ex}")
    finally:
        if conn:
            conn.close()

def listarVI(tipoConexao):
    conn = conexaoBD(tipoConexao)
    if not conn:
        return
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT pais, COUNT(pais) as conflitos
                FROM conflitopais
                NATURAL JOIN conflito
                WHERE tipoconf='Religioso'
                GROUP BY pais 
                ORDER BY conflitos
                LIMIT 1
                """
            )
            dados = cur.fetchall()

            df = pd.DataFrame(dados, columns=["País", 'Número de Conflitos Religiosos'])
            st.dataframe(df, use_container_width=False)
    except Exception as ex:
        st.error(f"Erro ao fazer listagem. ${ex}")
    finally:
        if conn:
            conn.close()
