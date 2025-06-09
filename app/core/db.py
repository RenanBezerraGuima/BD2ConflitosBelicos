import streamlit as st
import psycopg
from pathlib import Path

# Documentação do biblioteca psycopg (PsycoticPostGree)
# https://www.psycopg.org/psycopg3/docs/basic/usage.html

# define a raiz 'app/' dinamicamente
BASE_DIR = Path(__file__).resolve().parent.parent  # app/core/.. → app/

def conexaoBD(TipoConexao):
    """Estabelece conexão com o banco de dados PostgreSQL com base no tipo especificado."""
    StringConexao = ""
    TipoConexaoErro = ""

    # A conexão é baseada na minha instalação do postgree local
    # Altere baseado na sua conexão
    if TipoConexao == "local":
        TipoConexaoErro = "LOCAL"
        StringConexao = """
            dbname=postgres
            user=postgres
            host=localhost
            password=123456
            """
    # Banco de dados hosteado na plataforma neon
    elif TipoConexao == "remoto":
        TipoConexaoErro = "REMOTO"
        StringConexao = "postgresql://neondb_owner:npg_tR8DcpdN1rAI@ep-bitter-tooth-a8mynly3-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
    else:
        st.error(f"Tipo de conexão desconhecido: {TipoConexao}")
        return None

    try:
        conexao = psycopg.connect(StringConexao)
        return conexao
    except psycopg.OperationalError as e:
        st.error(f"Erro ao conectar ao banco de dados {TipoConexaoErro}: {e}")
        return None

def ResetarBD(TipoConexao):
    conn = conexaoBD(TipoConexao)
    if conn is None:
        st.error("Falha ao obter conexão para resetar o banco de dados.")
        return

    caminho = BASE_DIR / "sql" / "schema.sql"
    try:
        with conn.cursor() as cur:
            with open(caminho, "r", encoding="utf-8") as f:
                sql = f.read()
                cur.execute(sql)
        conn.commit()
        st.success("Script SQL de reset executado com sucesso.")
    except Exception as e:
        st.error(f"Erro ao executar script SQL de reset: {e}")
    finally:
        if conn:
            conn.close()
            
def DeletarBD(TipoConexao):
    conn = conexaoBD(TipoConexao)
    if conn is None:
        st.error("Falha ao obter conexão para resetar o banco de dados.")
        return
    
    caminho = BASE_DIR / "sql" / "delete.sql"
    try:
        with conn.cursor() as cur:
            with open(caminho, "r", encoding="utf-8") as f:
                sql = f.read()
                cur.execute(sql)
        conn.commit()
        st.success("Todas as tuplas do BD foram deletadas.")
    except Exception as e:
        st.error(f"Erro ao deleter as tuplas: {e}")
    finally:
        if conn:
            conn.close()
