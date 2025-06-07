import streamlit as st
import psycopg
import matplotlib.pyplot as plt
import pandas as pd
import datetime

# Documentação do biblioteca psycopg (PsycoticPostGre)
# https://www.psycopg.org/psycopg3/docs/basic/usage.html

# Documentação da biblioteca de interface streamlit
# https://docs.streamlit.io/

# Os campos da conexão dependem da
# conexão e do usuário do postgreSQL
def conexaoBD():
    """Estabelece conexão com o banco de dados PostgreSQL"""
    try:
        # Parâmetros dependem
        # do usuário e da conexão
        # com o banco de dados
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

def gerarHistograma():
    """Gera histograma de tipos de conflito"""
    conn = conexaoBD()
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
            # Cores para cada tipo de conflito
            bars = ax.bar(tipos, contagens, color=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"])

            # Quantida de conflitos acima da barra
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

def BuscarDivisoes(conn, CodigoG_selecionado=None): # Renomeado de fetch_divisoes
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
            # Retorna um dicionário com uma string descritiva como chave e (NroDivisao, CodigoG) como valor
            return {f"Divisão {nro} (Grupo: {nome_grupo})": (nro, cod_g) for nro, cod_g, nome_grupo in cur.fetchall()}
    except Exception as e:
        st.error(f"Erro ao buscar divisões: {e}")
        return {}

def BuscarPaises(conn): # Para ConflitoPais
    # Idealmente, você teria uma tabela Pais distinta.
    # Por agora, vamos supor que você queira inserir novos nomes de países.
    # Ou, se você tiver uma lista predefinida, pode usá-la.
    # Para este exemplo, vamos permitir a entrada de texto.
    pass # Será tratado com st.text_area ou st.multiselect com options dinâmicas

def BuscarConflitos(conn):
    """Busca todos os conflitos cadastrados"""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT CodConflito, Nome FROM Conflito ORDER BY Nome;")
            resultados = cur.fetchall()
            return {nome: codigo for codigo, nome in resultados} # {NomeConflito: CodConflito}
    except Exception as e:
        st.error(f"Erro ao buscar conflitos: {e}")
        return {}

def InserirGrupoArmado(conn):
    """Interface para inserção de novo grupo armado no banco de dados"""
    st.subheader("🎖️ Inserção de Novo Grupo Armado")

    # Form = Formulário
    with st.form("Formulário Grupo Armado", clear_on_submit=True):
        NomeGrupo = st.text_input(
           "Nome do Grupo Armado:",
           placeholder="Ex: Coalizão do Norte",
           help="Nome único para identificar o grupo armado"
        )

        submitted = st.form_submit_button("Inserir Grupo Armado", type="primary")

        if submitted:
            if NomeGrupo:
                try:
                    with conn.cursor() as cur:
                        cur.execute("INSERT INTO GrupoArmado (NomeGrupo) VALUES (%s) RETURNING CodigoG;", (NomeGrupo,))
                        cod_g_novo = cur.fetchone()[0]
                        conn.commit()
                    st.success(f"Grupo Armado '{NomeGrupo}' cadastrado com sucesso! Código: {cod_g_novo}")
                except psycopg.IntegrityError:
                    conn.rollback()
                    st.error(f"Erro: Grupo Armado com nome '{NomeGrupo}' já existe.")
                except Exception as e:
                    conn.rollback()
                    st.error(f"Erro ao cadastrar Grupo Armado: {e}")
            else:
                st.warning("O nome do grupo armado é obrigatório.")

def InserirParticipacaoConflito(conn):
    """Interface para inserção da participação de um grupo armado em um conflito"""
    st.subheader("🤝 Inserir a Participação de Grupo Armado em Conflito")

    GruposArmados = BuscarGruposArmados(conn) # {NomeGrupo: CodigoG}
    conflitos = BuscarConflitos(conn) # {NomeConflito: CodConflito}

    if not GruposArmados:
        st.warning("Nenhum grupo armado cadastrado. Cadastre um grupo primeiro.")
        return
    if not conflitos:
        st.warning("Nenhum conflito cadastrado. Cadastre um conflito primeiro.")
        return

    with st.form("Formulário de Participação de Conflitos", clear_on_submit=True):
        NomeGrupoSelecionado = st.selectbox(
            "Selecione o Grupo Armado:",
            options=list(GruposArmados.keys()),
            index=None,
            placeholder="Escolha um grupo",
            key="pc_grupo"
        )
        NomeConflitoSelecionado = st.selectbox(
            "Selecione o Conflito:",
            options=list(conflitos.keys()),
            index=None,
            placeholder="Escolha um conflito",
            key="pc_conflito"
        )
        DataEntrada = st.date_input(
            "Data de Entrada no Conflito:",
            key="pc_DataEntrada",
            format="DD/MM/YYYY",
            min_value=datetime.date(1,1,1),
            max_value="today"
        )
        DataSaida = st.date_input(
            "Data de Saída do Conflito (opcional):",
            value=None,
            key="pc_DataSaida",
            format="DD/MM/YYYY",
            max_value="today"
        )

        submitted = st.form_submit_button("Registrar Participação", type="primary")
        if submitted:
            if NomeGrupoSelecionado and NomeConflitoSelecionado and DataEntrada:
                CodigoG = GruposArmados[NomeGrupoSelecionado]
                CodigoConflito = conflitos[NomeConflitoSelecionado]

                if DataSaida and DataSaida < DataEntrada:
                    st.error("A data de saída não pode ser anterior à data de entrada.")
                    return
                
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            """INSERT INTO EntPart (CodigoG, CodConflito, DEGrupo, DSGrupo)
                            VALUES (%s, %s, %s, %s) RETURNING IdEntPart;""",
                            (CodigoG, CodigoConflito, DataEntrada, DataSaida)
                        )
                        id_ent_part = cur.fetchone()[0]
                        conn.commit()
                    st.success(f"Participação do grupo '{NomeGrupoSelecionado}' no conflito '{NomeConflitoSelecionado}' registrada com sucesso! ID: {id_ent_part}")
                except psycopg.IntegrityError as ie:
                    conn.rollback()
                    st.error(f"Erro de integridade: Verifique se esta participação já existe ou se os códigos são válidos. Detalhes: {ie}")
                except Exception as e:
                    conn.rollback()
                    st.error(f"Erro ao registrar participação: {e}")
            else:
                st.warning("Grupo armado, conflito e data de entrada são obrigatórios.")

def InserirLiderPolitico(conn):
    """Interface para a inserção de um novo líder político no banco de dados"""
    st.subheader("👨‍💼 Inserção de Novo Líder Político")
    
    with st.form("Formulário Líder Político", clear_on_submit=True):
        NomeLider = st.text_input("Nome do Líder Político:", key="lp_nome")
        ApoiosLider = st.text_area("Apoios do Líder:", key="lp_apoios")

        GruposArmadosDic = BuscarGruposArmados(conn) # {NomeGrupo: CodigoG}
        if GruposArmadosDic:
            ListaNomesGrupos = list(GruposArmadosDic.keys())
            if not ListaNomesGrupos:
                st.warning("Nenhum grupo armado cadastrado. Cadastre um grupo primeiro.")
                return

            NomeGrupoSelecionado = st.selectbox(
                "Selecione o Grupo Armado do Líder:",
                options=ListaNomesGrupos,
                key="lp_grupo",
                index=None,
                placeholder="Escolha um grupo"
            )
            
            submitted = st.form_submit_button("Inserir Líder Político", type="primary")
            if submitted:
                if NomeLider and NomeGrupoSelecionado:
                    CodigoGLider = GruposArmadosDic[NomeGrupoSelecionado]
                    try:
                        with conn.cursor() as cur:
                            cur.execute(
                                "INSERT INTO LiderPolitico (NomeL, CodigoG, Apoios) VALUES (%s, %s, %s);",
                                (NomeLider, CodigoGLider, ApoiosLider if ApoiosLider else None)
                            )
                            conn.commit()
                        st.success(f"Líder Político '{NomeLider}' cadastrado com sucesso!")
                    except psycopg.IntegrityError:
                        conn.rollback()
                        st.error(f"Erro: Líder Político com nome '{NomeLider}' já existe ou violação de chave estrangeira.")
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Erro ao cadastrar Líder Político: {e}")
                else:
                    st.warning("Nome do líder e grupo armado são obrigatórios.")
        else:
            st.warning("Nenhum grupo armado cadastrado. Cadastre um grupo primeiro.")
            return

def InserirDivisaoMilitar(conn):
    st.subheader("🏗️ Inserção de Nova Divisão Militar")
    with st.form("Formulario_Divisao_Militar", clear_on_submit=True):
        GruposArmadosDic = BuscarGruposArmados(conn) # {NomeGrupo: CodigoG}
        
        if not GruposArmadosDic:
            st.warning("Nenhum grupo armado cadastrado. Cadastre um grupo primeiro.")
            return

        lista_nomes_grupos_div = list(GruposArmadosDic.keys())
        nome_grupo_div_selecionado = st.selectbox(
            "Selecione o Grupo Armado da Divisão:",
            options=lista_nomes_grupos_div,
            index=None,
            placeholder="Escolha um grupo"
        )
        
        NumeroBaixasDivisao = st.number_input("Número de Baixas da Divisão:", min_value=0)
        
        # Divisão em 2 colunas
        col1, col2 = st.columns(2)
        
        barcos = col1.number_input("Número de Barcos:", min_value=0)
        tanques = col1.number_input("Número de Tanques:", min_value=0)
        
        avioes = col2.number_input("Número de Aviões:", min_value=0)
        homens = col2.number_input("Número de Homens:", min_value=0)

        submitted = st.form_submit_button("Inserir Divisão", type="primary")
        if submitted:
            if nome_grupo_div_selecionado and homens > 0 :
                CodigoG_div = GruposArmadosDic[nome_grupo_div_selecionado]
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            """INSERT INTO Divisao (CodigoG, NumBaixasD, Barcos, Tanques, Avioes, Homens)
                            VALUES (%s, %s, %s, %s, %s, %s) RETURNING NroDivisao;""",
                            (CodigoG_div, NumeroBaixasDivisao, barcos, tanques, avioes, homens) # Adicionado NumeroBaixasDivisao
                        )
                        nro_div_novo = cur.fetchone()[0]
                        conn.commit()
                    st.success(f"Divisão Nº{nro_div_novo} para o grupo '{nome_grupo_div_selecionado}' cadastrada com sucesso!")
                except Exception as e:
                    conn.rollback()
                    st.error(f"Erro ao cadastrar Divisão: {e}.")
            elif not nome_grupo_div_selecionado:
                st.warning("O grupo armado é obrigatório.")
            elif homens <= 0:
                st.warning("O número de homens deve ser maior que zero.")
            else:
                st.warning("Preencha os campos obrigatórios.")


def InserirChefeMilitar(conn):
    st.subheader("🎖️ Inserção de Novo Chefe Militar")
    with st.form("Formulario_Chefe_Militar", clear_on_submit=True):
        faixa_chefe = st.text_input("Faixa do Chefe Militar:")

        DivisoesDic = BuscarDivisoes(conn) # {DescricaoDivisao: (NroDivisao, CodigoG)}
        lideres_politicos_list = BuscarLideresPoliticos(conn) # Lista de NomeL

        if not DivisoesDic:
            st.warning("Nenhuma divisão cadastrada. Cadastre uma divisão primeiro.")
            return
        if not lideres_politicos_list:
            st.warning("Nenhum líder político cadastrado. Cadastre um líder primeiro.")
            return
        
        lista_desc_divisoes = list(DivisoesDic.keys())
        DivisaoLiderada = st.selectbox(
            "Selecione a Divisão liderada pelo Chefe Militar:",
            options=lista_desc_divisoes,
            placeholder="Escolha uma divisão"
        )
        NomeLider = st.selectbox(
            "Selecione o Líder Político que o Chefe obedece:",
            options=lideres_politicos_list,
            placeholder="Escolha um líder"
        )
        
        submitted = st.form_submit_button("Inserir Chefe Militar", type="primary")
        if submitted:
            if faixa_chefe and DivisaoLiderada and NomeLider:
                nro_div_cm, CodigoG_cm = DivisoesDic[DivisaoLiderada]
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            """INSERT INTO ChefeMilitar (Faixa, NroDivisao, CodigoG, NomeL)
                            VALUES (%s, %s, %s, %s) RETURNING codigoChef;""",
                            (faixa_chefe, nro_div_cm, CodigoG_cm, NomeLider)
                        )
                        cod_chef_novo = cur.fetchone()[0]
                        conn.commit()
                    st.success(f"Chefe Militar (Código: {cod_chef_novo}, Faixa: {faixa_chefe}) cadastrado com sucesso!")
                except Exception as e: # Triggers podem causar erros (ex: max 3 chefes, líder não pertence ao grupo)
                    conn.rollback()
                    st.error(f"Erro ao cadastrar Chefe Militar: {e}")
            else:
                st.warning("Todos os campos são obrigatórios.")

def InserirConflitoBelico(conn):
    st.subheader("⚔️ Inserção de Novo Conflito Bélico")
    
    TiposDeConflito = ["Territorial", "Religioso", "Econômico", "Racial"]

    with st.form("Formulário Conflito Bélico", clear_on_submit=True):
        # Divisão em duas colunas para os primeiros 4 campos
        col1, col2 = st.columns(2)
        
        NomeConflito = col1.text_input("Nome do Conflito:", placeholder="Guerra do Norte")
        
        TipoEscolhido = col1.selectbox(
            "Tipo de Conflito:", 
            options=TiposDeConflito,
            index=None,
            placeholder="Escolha um tipo"
        )
        
        NumeroFeridos = col2.number_input("Número de Feridos:", min_value=0, step=100)
        NumeroMortos = col2.number_input("Número de Mortos:", min_value=0, step=100)

        DetalhesTipoConflito = st.text_area(
            label="Detalhes Específicos do Tipo de Conflito separados por vírgula (Ex: Regiões ou Religiões ou Mat. Primas ou Etnias):",
            placeholder="Ex: Detalhe A, Detalhe B, Detalhe C"
        )

        PaisesEnvolvidos = st.text_area(
            "Países Envolvidos (separados por vírgula):",
            help="Ex: Brasil, Argentina, Uruguai",
            placeholder="Brasil, Argentina, Uruguai, Paraguai"
        )

        submitted = st.form_submit_button("Inserir Conflito Bélico", type="primary")
        if submitted:
            if NomeConflito and TipoEscolhido and DetalhesTipoConflito:
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            "INSERT INTO Conflito (Nome, NumFeridos, NumMortos, TipoConf) VALUES (%s, %s, %s, %s) RETURNING CodConflito;",
                            (NomeConflito, NumeroFeridos, NumeroMortos, TipoEscolhido)
                        )
                        CodNovoConflito = cur.fetchone()[0]

                        # Processamento dos múltiplos detalhes
                        ListaDetalhes = [det.strip() for det in DetalhesTipoConflito.split(',') if det.strip()] 
                            
                        # Escolhas de Tipo
                        if TipoEscolhido == "Territorial":
                            for detalhe in ListaDetalhes:
                                cur.execute("INSERT INTO Territorial (CodConflito, Regiao) VALUES (%s, %s);", (CodNovoConflito, detalhe))
                        elif TipoEscolhido == "Religioso":
                            for detalhe in ListaDetalhes:
                                cur.execute("INSERT INTO Religioso (CodConflito, Religiao) VALUES (%s, %s);", (CodNovoConflito, detalhe))
                        elif TipoEscolhido == "Econômico":
                            for detalhe in ListaDetalhes:
                                cur.execute("INSERT INTO Econômico (CodConflito, MatPrima) VALUES (%s, %s);", (CodNovoConflito, detalhe))
                        elif TipoEscolhido == "Racial":
                            for detalhe in ListaDetalhes:
                                cur.execute("INSERT INTO Racial (CodConflito, Etnia) VALUES (%s, %s);", (CodNovoConflito, detalhe))

                        if PaisesEnvolvidos:
                            lista_paises = [pais.strip() for pais in PaisesEnvolvidos.split(',') if pais.strip()]
                            for pais in lista_paises:
                                cur.execute("INSERT INTO ConflitoPais (CodConflito, Pais) VALUES (%s, %s);", (CodNovoConflito, pais))
                        conn.commit()
                    st.success(f"Conflito '{NomeConflito}' (Código: {CodNovoConflito}) cadastrado com sucesso!")
                except Exception as e:
                    conn.rollback()
                    st.error(f"Erro ao cadastrar Conflito Bélico: {e}")
            elif not NomeConflito:
                st.warning("Nome do conflito deve ser preenchido especificado.")
            elif not TipoEscolhido:
                st.warning("Tipo de conflito deve ser selecionado.")
            elif not DetalhesTipoConflito:
                st.warning("Detalhes sobre o tipo de conflito devem ser preenchidos.")
            else:
                st.warning("Nome, tipo de conflito e o detalhe específico do tipo são obrigatórios.")

def main():
    # Configuração da Página (Nome e ícone da aba no navegador)
    st.set_page_config(
        page_title="Conflitos BélicosBD",
        page_icon="⚔️",
        layout="wide",
    )
    st.title("⚔️ Conflitos BélicosBD")

    # Abas principais da aplicação
    tabInsercoes, tabConsultas = st.tabs(["📝 Inserções", "📊 Consultas"])

    with tabInsercoes:
        st.header("Inserções de Novos Dados")

        # Opções de inserções
        opcoesInsercao = [
            "Grupo Armado",
            "Participação em Conflito",
            "Líder Político",
            "Divisão Militar",
            "Chefe Militar",
            "Conflito Bélico",
        ]

        # Linha de escolhas de inserções
        escolha = st.segmented_control(
            "Selecione o tipo de dados para inserir:",
            opcoesInsercao,
            selection_mode="single"
        )

        conn = conexaoBD()
        if  not conn:
            # conexaoBD já mostra erro
            return

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
            conn.close()

    with tabConsultas:
        st.header("📊 Consultas no Banco de Dados")

        st.subheader("Histograma de Tipos de Conflito")
        st.write("Visualize a distribuição dos conflitos por tipo")

        if st.button("Gerar Histograma", type="primary"):
            with st.spinner("Gerando Histrograma..."):
                gerarHistograma()

if __name__ == "__main__":
    main()
