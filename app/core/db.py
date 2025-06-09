import streamlit as st
import psycopg
from pathlib import Path

# define a raiz 'app/' dinamicamente
BASE_DIR = Path(__file__).resolve().parent.parent  # app/core/.. → app/

def conexaoBD(TipoConexao):
    # … sua implementação atual …
    pass

def ResetarBD(TipoConexao):
    conn = conexaoBD(TipoConexao)
    if conn is None:
        st.error("Falha ao obter conexão para resetar o banco de dados.")
        return

    sql_file = BASE_DIR / "sql" / "schema.sql"
    try:
        with conn.cursor() as cur, open(sql_file, "r", encoding="utf-8") as f:
            cur.execute(f.read())
        conn.commit()
        st.success("Script SQL de reset executado com sucesso.")
    except FileNotFoundError:
        st.error(f"Arquivo não encontrado: {sql_file}")
    except Exception as e:
        st.error(f"Erro ao executar script SQL de reset: {e}")
    finally:
        conn.close()

def DeletarBD(TipoConexao):
    conn = conexaoBD(TipoConexao)
    if conn is None:
        st.error("Falha ao obter conexão para deletar as tuplas do banco de dados.")
        return

    sql_file = BASE_DIR / "sql" / "delete.sql"
    try:
        with conn.cursor() as cur, open(sql_file, "r", encoding="utf-8") as f:
            cur.execute(f.read())
        conn.commit()
        st.success("Todas as tuplas do BD foram deletadas.")
    except FileNotFoundError:
        st.error(f"Arquivo não encontrado: {sql_file}")
    except Exception as e:
        st.error(f"Erro ao deletar as tuplas: {e}")
    finally:
        conn.close()