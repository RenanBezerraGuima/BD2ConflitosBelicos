import streamlit as st
import psycopg
import matplotlib.pyplot as plt

# Documentação do biblioteca psycopg (PsycoticPostGre)
# https://www.psycopg.org/psycopg3/docs/basic/usage.html

# Os campos da conexão dependem da
# conexão e do usuário do postgreSQL
def conexaoBD():
    # IMPORTANTE: Feche a conexão após o uso ou use 'with' para garantir o fechamento.
    try:
        conexao = psycopg.connect(
            """
            dbname=postgres
            user=postgres
            host=localhost
            password=123456
            """
        )
        return conexao
    except psycopg.OperationalError as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def gerarHistograma(): # Removido cursor como argumento, será obtido internamente
    conn = conexaoBD()
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
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
            st.info("Não há dados sobre conflitos para gerar este histograma!")
    except Exception as e:
        st.error(f"Erro ao gerar histograma: {e}")
    finally:
        if conn:
            conn.close()

# --- Funções para buscar dados para Selectbox (FKs) ---
def fetch_grupos_armados(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT CodigoG, NomeGrupo FROM GrupoArmado ORDER BY NomeGrupo;")
        return {nome: codigo for codigo, nome in cur.fetchall()}

def fetch_lideres_politicos(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT NomeL FROM LiderPolitico ORDER BY NomeL;")
        return [row[0] for row in cur.fetchall()]

def fetch_divisoes(conn, codigo_g_selecionado=None): # Aceita CodigoG para filtrar
    with conn.cursor() as cur:
        if codigo_g_selecionado:
            cur.execute("""
                SELECT D.NroDivisao, D.CodigoG, GA.NomeGrupo
                FROM Divisao D
                JOIN GrupoArmado GA ON D.CodigoG = GA.CodigoG
                WHERE D.CodigoG = %s
                ORDER BY GA.NomeGrupo, D.NroDivisao;
            """, (codigo_g_selecionado,))
            return {f"Divisão {nro} (Grupo: {nome_grupo})": (nro, cod_g) for nro, cod_g, nome_grupo in cur.fetchall()}
        else:
            cur.execute("""
                SELECT D.NroDivisao, D.CodigoG, GA.NomeGrupo
                FROM Divisao D
                JOIN GrupoArmado GA ON D.CodigoG = GA.CodigoG
                ORDER BY GA.NomeGrupo, D.NroDivisao;
            """)
            # Retorna um dicionário com uma string descritiva como chave e (NroDivisao, CodigoG) como valor
            return {f"Divisão {nro} (Grupo: {nome_grupo})": (nro, cod_g) for nro, cod_g, nome_grupo in cur.fetchall()}


def fetch_paises(conn): # Para ConflitoPais
    # Idealmente, você teria uma tabela Pais distinta.
    # Por agora, vamos supor que você queira inserir novos nomes de países.
    # Ou, se você tiver uma lista predefinida, pode usá-la.
    # Para este exemplo, vamos permitir a entrada de texto.
    pass # Será tratado com st.text_area ou st.multiselect com options dinâmicas

st.title("Conflitos BélicosBD")

tabInsercoes, tabConsultas = st.tabs(["Inserções", "Consultas"])

with tabInsercoes:
    st.header("Inserções de Novos Dados")
    opcoesInsercao = ["Grupo Militar", "Líder Político", "Divisão Militar", "Chefe Militar", "Conflito Bélico"]
    # Usando st.radio para melhor visualização vertical das opções de cadastro
    escolha = st.radio("Escolha abaixo qual dado deseja inserir no banco de dados:", opcoesInsercao, horizontal=False)

    conn_insert = conexaoBD() # Abrir conexão para operações de inserção
    if conn_insert: # Procede apenas se a conexão foi bem-sucedida
        if escolha == "Grupo Militar":
            st.subheader("Cadastrar Novo Grupo Militar")
            nome_grupo = st.text_input("Nome do Grupo Militar:", key="gm_nome")
            if st.button("Cadastrar Grupo Militar", key="btn_gm"):
                if nome_grupo:
                    try:
                        with conn_insert.cursor() as cur:
                            cur.execute("INSERT INTO GrupoArmado (NomeGrupo) VALUES (%s) RETURNING CodigoG;", (nome_grupo,))
                            cod_g_novo = cur.fetchone()[0]
                            conn_insert.commit()
                        st.success(f"Grupo Militar '{nome_grupo}' cadastrado com sucesso! Código: {cod_g_novo}")
                    except Exception as e:
                        conn_insert.rollback()
                        st.error(f"Erro ao cadastrar Grupo Militar: {e}")
                else:
                    st.warning("O nome do grupo militar é obrigatório.")

        elif escolha == "Líder Político":
            st.subheader("Cadastrar Novo Líder Político")
            nome_lider = st.text_input("Nome do Líder Político:", key="lp_nome")
            apoios_lider = st.text_area("Apoios do Líder:", key="lp_apoios")

            grupos_armados_dict = fetch_grupos_armados(conn_insert)
            if grupos_armados_dict:
                nome_grupo_selecionado = st.selectbox(
                    "Selecione o Grupo Armado do Líder:",
                    options=list(grupos_armados_dict.keys()),
                    key="lp_grupo"
                )
                if st.button("Cadastrar Líder Político", key="btn_lp"):
                    if nome_lider and nome_grupo_selecionado:
                        codigo_g_lider = grupos_armados_dict[nome_grupo_selecionado]
                        try:
                            with conn_insert.cursor() as cur:
                                cur.execute(
                                    "INSERT INTO LiderPolitico (NomeL, CodigoG, Apoios) VALUES (%s, %s, %s);",
                                    (nome_lider, codigo_g_lider, apoios_lider)
                                )
                                conn_insert.commit()
                            st.success(f"Líder Político '{nome_lider}' cadastrado com sucesso!")
                        except Exception as e:
                            conn_insert.rollback()
                            st.error(f"Erro ao cadastrar Líder Político: {e}")
                    else:
                        st.warning("Nome do líder e grupo armado são obrigatórios.")
            else:
                st.warning("Nenhum grupo armado cadastrado. Cadastre um grupo primeiro.")


        elif escolha == "Divisão Militar":
            st.subheader("Cadastrar Nova Divisão Militar")
            grupos_armados_dict_div = fetch_grupos_armados(conn_insert)
            if grupos_armados_dict_div:
                nome_grupo_div_selecionado = st.selectbox(
                    "Selecione o Grupo Armado da Divisão:",
                    options=list(grupos_armados_dict_div.keys()),
                    key="div_grupo"
                )
                barcos = st.number_input("Número de Barcos:", min_value=0, step=1, key="div_barcos")
                tanques = st.number_input("Número de Tanques:", min_value=0, step=1, key="div_tanques")
                avioes = st.number_input("Número de Aviões:", min_value=0, step=1, key="div_avioes")
                homens = st.number_input("Número de Homens:", min_value=0, step=1, key="div_homens")

                if st.button("Cadastrar Divisão", key="btn_div"):
                    if nome_grupo_div_selecionado:
                        codigo_g_div = grupos_armados_dict_div[nome_grupo_div_selecionado]
                        try:
                            with conn_insert.cursor() as cur:
                                # NroDivisao é SERIAL, NumBaixasD tem DEFAULT 0
                                cur.execute(
                                    """INSERT INTO Divisao (CodigoG, Barcos, Tanques, Avioes, Homens)
                                       VALUES (%s, %s, %s, %s, %s) RETURNING NroDivisao;""",
                                    (codigo_g_div, barcos, tanques, avioes, homens)
                                )
                                nro_div_novo = cur.fetchone()[0]
                                conn_insert.commit()
                            st.success(f"Divisão Nº{nro_div_novo} para o grupo '{nome_grupo_div_selecionado}' cadastrada com sucesso!")
                        except Exception as e:
                            conn_insert.rollback()
                            st.error(f"Erro ao cadastrar Divisão: {e}. Verifique se os triggers (ex: sequencialidade) estão implementados no BD.")
                    else:
                        st.warning("O grupo armado é obrigatório.")
            else:
                st.warning("Nenhum grupo armado cadastrado. Cadastre um grupo primeiro.")

        elif escolha == "Chefe Militar":
            st.subheader("Cadastrar Novo Chefe Militar")
            faixa_chefe = st.text_input("Faixa do Chefe Militar:", key="cm_faixa")

            divisoes_dict = fetch_divisoes(conn_insert) # Pega todas as divisões
            lideres_politicos_list = fetch_lideres_politicos(conn_insert)

            if divisoes_dict and lideres_politicos_list:
                divisao_desc_selecionada = st.selectbox(
                    "Selecione a Divisão do Chefe:",
                    options=list(divisoes_dict.keys()),
                    key="cm_divisao"
                )
                nome_lider_obedece = st.selectbox(
                    "Selecione o Líder Político que o Chefe obedece:",
                    options=lideres_politicos_list,
                    key="cm_lider_obedece"
                )
                if st.button("Cadastrar Chefe Militar", key="btn_cm"):
                    if faixa_chefe and divisao_desc_selecionada and nome_lider_obedece:
                        nro_div_cm, codigo_g_cm = divisoes_dict[divisao_desc_selecionada]
                        try:
                            with conn_insert.cursor() as cur:
                                # codigoChef é SERIAL
                                cur.execute(
                                    """INSERT INTO ChefeMilitar (Faixa, NroDivisao, CodigoG, NomeL)
                                       VALUES (%s, %s, %s, %s) RETURNING codigoChef;""",
                                    (faixa_chefe, nro_div_cm, codigo_g_cm, nome_lider_obedece)
                                )
                                cod_chef_novo = cur.fetchone()[0]
                                conn_insert.commit()
                            st.success(f"Chefe Militar (Código: {cod_chef_novo}, Faixa: {faixa_chefe}) cadastrado com sucesso!")
                        except Exception as e:
                            conn_insert.rollback()
                            # Erros podem vir dos triggers (ex: max 3 chefes por divisão)
                            st.error(f"Erro ao cadastrar Chefe Militar: {e}")
                    else:
                        st.warning("Todos os campos são obrigatórios.")
            else:
                st.warning("É necessário ter Divisões e Líderes Políticos cadastrados.")

        elif escolha == "Conflito Bélico":
            st.subheader("Cadastrar Novo Conflito Bélico")
            nome_conflito = st.text_input("Nome do Conflito:", key="cb_nome")
            num_feridos = st.number_input("Número de Feridos:", min_value=0, step=1, key="cb_feridos")
            num_mortos = st.number_input("Número de Mortos:", min_value=0, step=1, key="cb_mortos")
            tipos_conflito_opts = ["Territorial", "Religioso", "Economico", "Racial"]
            tipo_conf_selecionado = st.selectbox("Tipo de Conflito:", tipos_conflito_opts, key="cb_tipo")

            # Campos específicos do tipo de conflito
            detalhe_tipo_conf = ""
            if tipo_conf_selecionado == "Territorial":
                detalhe_tipo_conf = st.text_input("Região Afetada:", key="cb_regiao")
            elif tipo_conf_selecionado == "Religioso":
                detalhe_tipo_conf = st.text_input("Religião Envolvida:", key="cb_religiao")
            elif tipo_conf_selecionado == "Economico":
                detalhe_tipo_conf = st.text_input("Matéria Prima Disputada:", key="cb_matprima")
            elif tipo_conf_selecionado == "Racial":
                detalhe_tipo_conf = st.text_input("Etnia Envolvida:", key="cb_etnia")

            paises_envolvidos_str = st.text_area(
                "Países Envolvidos (separados por vírgula):",
                key="cb_paises",
                help="Ex: Brasil, Argentina, Uruguai"
            )

            if st.button("Cadastrar Conflito Bélico", key="btn_cb"):
                if nome_conflito and tipo_conf_selecionado and (tipo_conf_selecionado and detalhe_tipo_conf): # Garante que detalhe foi preenchido
                    try:
                        with conn_insert.cursor() as cur:
                            # 1. Inserir na tabela Conflito
                            cur.execute(
                                "INSERT INTO Conflito (Nome, NumFeridos, NumMortos, TipoConf) VALUES (%s, %s, %s, %s) RETURNING CodConflito;",
                                (nome_conflito, num_feridos, num_mortos, tipo_conf_selecionado)
                            )
                            cod_conf_novo = cur.fetchone()[0]

                            # 2. Inserir na tabela específica do tipo de conflito
                            if tipo_conf_selecionado == "Territorial":
                                cur.execute("INSERT INTO Territorial (CodConflito, Regiao) VALUES (%s, %s);", (cod_conf_novo, detalhe_tipo_conf))
                            elif tipo_conf_selecionado == "Religioso":
                                cur.execute("INSERT INTO Religioso (CodConflito, Religiao) VALUES (%s, %s);", (cod_conf_novo, detalhe_tipo_conf))
                            elif tipo_conf_selecionado == "Economico":
                                cur.execute("INSERT INTO Economico (CodConflito, MatPrima) VALUES (%s, %s);", (cod_conf_novo, detalhe_tipo_conf))
                            elif tipo_conf_selecionado == "Racial":
                                cur.execute("INSERT INTO Racial (CodConflito, Etnia) VALUES (%s, %s);", (cod_conf_novo, detalhe_tipo_conf))

                            # 3. Inserir países em ConflitoPais
                            if paises_envolvidos_str:
                                lista_paises = [pais.strip() for pais in paises_envolvidos_str.split(',') if pais.strip()]
                                for pais in lista_paises:
                                    cur.execute("INSERT INTO ConflitoPais (CodConflito, Pais) VALUES (%s, %s);", (cod_conf_novo, pais))
                            conn_insert.commit()
                        st.success(f"Conflito '{nome_conflito}' (Código: {cod_conf_novo}) cadastrado com sucesso!")
                    except Exception as e:
                        conn_insert.rollback()
                        st.error(f"Erro ao cadastrar Conflito Bélico: {e}")
                else:
                    st.warning("Nome, tipo de conflito e o detalhe específico do tipo são obrigatórios.")
        # Fechar a conexão após todas as operações de inserção da aba
        if conn_insert:
            conn_insert.close()

with tabConsultas:
    st.header("Consultas no Banco de Dados")
    st.subheader("Histograma de Tipos de Conflito")
    if st.button("Gerar Histograma", type="primary", key="btn_hist"):
        gerarHistograma() # Chama a função que agora gerencia sua própria conexão
