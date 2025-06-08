# Depêndencias
Python, pip e as seguintes depêndencias devem ser instaladas para executar o código fonte:
```bash
pip install --upgrade pip
pip install streamlit
pip install "psycopg[binary,pool]"  # to install package and dependencies
pip install matplotlib
```

# Execução
Para executar a aplicação com um banco de dados local:
```bash
streamlit run app/local.py
```

Para executar a aplicação com um banco de dados remoto:
```bash
streamlit run app/remote.py
```

Para interagir com uma aplicação que executa remotamente em um banco de dados remoto:
https://conflitosbelicosbd.streamlit.app/

# Estrutura do Projeto
A aplicação principal está localizada em `app/core`.
- `app.py`: Lógica da aplicação principal e interface via Streamlit.
- `db.py`: Conexão com o banco de dados e execução de script.
- `queries.py`: Funções de busca de dados do banco de dados.
- `inserts.py`: Funções para inserções de dados no banco de dados.
- `plot.py`: Geração de plot para visualização dos dados.

Esquema do banco de dados:
- `data/sql/schema.sql`: Script SQL para criação e população do banco de dados.

Documentação:
- `docs/`
