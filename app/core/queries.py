import streamlit as st
import psycopg

# Funções de busca de dados (Chaves Estrangeiras)
def BuscarGruposArmados(conn):
    """Busca todos os grupos armados do banco de dados"""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT CodigoG, NomeGrupo FROM GrupoArmado ORDER BY NomeGrupo;")
            resultados = cur.fetchall()
            return {nome: codigo for codigo, nome in resultados}
    except Exception as e:
        st.error(f"Erro ao buscar grupos armados: {e}")
        return {}

def BuscarLideresPoliticos(conn):
    """Busca todos os líderes políticos do banco de dados"""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT NomeL FROM LiderPolitico ORDER BY NomeL;")
            resultados = cur.fetchall()
            return [row[0] for row in resultados]
    except Exception as e:
        st.error(f"Erro ao buscar líderes políticos: {e}")
        return []

def BuscarDivisoes(conn, CodigoG_selecionado=None):
    """Busca divisões, opcionalmente filtradas por grupo armado"""
    try:
        with conn.cursor() as cur:
            if CodigoG_selecionado:
                cur.execute("""
                    SELECT D.NroDivisao, D.CodigoG, GA.NomeGrupo
                    FROM Divisao D
                    JOIN GrupoArmado GA ON D.CodigoG = GA.CodigoG
                    WHERE D.CodigoG = %s
                    ORDER BY D.NroDivisao, GA.NomeGrupo;
                """, (CodigoG_selecionado,))
            else:
                cur.execute("""
                    SELECT D.NroDivisao, D.CodigoG, GA.NomeGrupo
                    FROM Divisao D
                    JOIN GrupoArmado GA ON D.CodigoG = GA.CodigoG
                    ORDER BY D.NroDivisao, GA.NomeGrupo;
                """)
            return {f"Divisão {nro} (Grupo: {nome_grupo})": (nro, cod_g) for nro, cod_g, nome_grupo in cur.fetchall()}
    except Exception as e:
        st.error(f"Erro ao buscar divisões: {e}")
        return {}

def BuscarPaises(conn):
    pass # Placeholder

def BuscarConflitos(conn):
    """Busca todos os conflitos cadastrados"""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT CodConflito, Nome FROM Conflito ORDER BY Nome;")
            resultados = cur.fetchall()
            return {nome: codigo for codigo, nome in resultados}
    except Exception as e:
        st.error(f"Erro ao buscar conflitos: {e}")
        return {}
