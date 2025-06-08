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
