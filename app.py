# app.py
import streamlit as st
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt

# ── Configuração da página ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Titanic Dashboard",
    page_icon="🚢",
    layout="wide"
)

# ── Funções de carregamento ────────────────────────────────────────────────────
@st.cache_data
def carregar_csv():
    return pd.read_csv('data/titanic.csv')

@st.cache_data
def carregar_banco():
    conn = sqlite3.connect('database/titanic.db')
    df = pd.read_sql('SELECT * FROM passageiros', conn)
    conn.close()
    return df

# ── Menu lateral ───────────────────────────────────────────────────────────────
st.sidebar.title("🚢 Titanic App")
st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Navegação",
    ["Início",
     "Dados do CSV",
     "Dados do Banco",
     "Visualização",
     "Sobre"]
)

# ── Páginas ────────────────────────────────────────────────────────────────────

# ── PÁGINA 1: INÍCIO ──────────────────────────────────────────────────────────
if pagina == "Início":
    st.title("Reuniao de final de ano")
    st.markdown("""
    Bem-vindo ao **Python para Ciência de Dados - Titanic Dashboard** — um exemplo prático de como construir
    uma aplicação de dados com **Streamlit** em Python.

    Este app demonstra como conectar diferentes fontes de dados
    e apresentar análises de forma interativa.
    """)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📂 **Fonte 1**\nArquivo CSV local")
    with col2:
        st.info("🗄️ **Fonte 2**\nBanco de dados SQLite")
    with col3:
        st.info("📊 **Fonte 3**\nVisualizações interativas")

    st.markdown("---")
    st.markdown("Use o menu lateral para navegar entre as seções.")

# ── PÁGINA 2: DADOS DO CSV ────────────────────────────────────────────────────
elif pagina == "Dados do CSV":
    st.title("📂 Dados do CSV")
    st.markdown("Dados carregados diretamente do arquivo `data/titanic.csv`.")

    df_csv = carregar_csv()

    # Métricas resumidas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de passageiros", len(df_csv))
    col2.metric("Sobreviventes",
                int(df_csv['survived'].sum()))
    col3.metric("Taxa de sobrevivência",
                f"{df_csv['survived'].mean():.1%}")
    col4.metric("Colunas disponíveis",
                len(df_csv.columns))

    st.markdown("---")

    # Filtro interativo
    st.subheader("Filtrar por classe")
    classes = sorted(df_csv['pclass'].dropna().unique())
    classe_sel = st.multiselect(
        "Selecione a(s) classe(s):",
        options=classes,
        default=classes
    )
    df_filtrado = df_csv[df_csv['pclass'].isin(classe_sel)]

    st.dataframe(df_filtrado, use_container_width=True)
    st.caption(f"{len(df_filtrado)} registros exibidos")

# ── PÁGINA 3: DADOS DO BANCO ──────────────────────────────────────────────────
elif pagina == "Dados do Banco":
    st.title("🗄️ Dados do Banco de Dados")
    st.markdown("Dados carregados via conexão com o banco **SQLite**.")

    st.code("""
# Exemplo de conexão — funciona com qualquer banco
# PostgreSQL: postgresql://usuario:senha@host:5432/banco
# MySQL:      mysql://usuario:senha@host:3306/banco
# SQLite:     sqlite:///database/titanic.db
conn = sqlite3.connect('database/titanic.db')
df = pd.read_sql('SELECT * FROM passageiros', conn)
    """, language='python')

    df_banco = carregar_banco()

    st.markdown("---")

    # Estatísticas descritivas
    st.subheader("Estatísticas descritivas")
    st.dataframe(df_banco.describe().round(2),
                 use_container_width=True)

    st.markdown("---")

    # Tabela com busca
    st.subheader("Explorar registros")
    col1, col2 = st.columns(2)
    with col1:
        sexo_sel = st.selectbox(
            "Filtrar por sexo:",
            options=["Todos", "male", "female"]
        )
    with col2:
        sobrev_sel = st.selectbox(
            "Filtrar por sobrevivência:",
            options=["Todos", "Sobreviveu (1)", "Não Sobreviveu (0)"]
        )

    df_banco_filtrado = df_banco.copy()
    if sexo_sel != "Todos":
        df_banco_filtrado = df_banco_filtrado[
            df_banco_filtrado['sex'] == sexo_sel]
    if sobrev_sel == "Sobreviveu (1)":
        df_banco_filtrado = df_banco_filtrado[
            df_banco_filtrado['survived'] == 1]
    elif sobrev_sel == "Não Sobreviveu (0)":
        df_banco_filtrado = df_banco_filtrado[
            df_banco_filtrado['survived'] == 0]

    st.dataframe(df_banco_filtrado, use_container_width=True)
    st.caption(f"{len(df_banco_filtrado)} registros exibidos")

# ── PÁGINA 4: VISUALIZAÇÃO ────────────────────────────────────────────────────
elif pagina == "Visualização":
    st.title("📊 Visualização")
    st.markdown("Gráficos interativos gerados a partir dos dados.")

    df_csv = carregar_csv()

    # Seletor de gráfico
    tipo_grafico = st.selectbox(
        "Escolha o tipo de gráfico:",
        ["Sobrevivência por Sexo",
         "Sobrevivência por Classe",
         "Distribuição de Idade",
         "Heatmap: Sexo × Classe"]
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.set_theme(style='whitegrid')

    if tipo_grafico == "Sobrevivência por Sexo":
        sns.barplot(data=df_csv, x='sex', y='survived',
                    palette='Blues', ax=ax)
        ax.set_title('Taxa de Sobrevivência por Sexo')
        ax.set_ylabel('Taxa de Sobrevivência')

    elif tipo_grafico == "Sobrevivência por Classe":
        sns.barplot(data=df_csv, x='pclass', y='survived',
                    palette='Blues', ax=ax)
        ax.set_title('Taxa de Sobrevivência por Classe')
        ax.set_ylabel('Taxa de Sobrevivência')

    elif tipo_grafico == "Distribuição de Idade":
        sns.histplot(data=df_csv, x='age', hue='survived',
                     bins=30, kde=True, palette='Blues', ax=ax)
        ax.set_title('Distribuição de Idade por Sobrevivência')
        ax.set_xlabel('Idade')

    elif tipo_grafico == "Heatmap: Sexo × Classe":
        pivot = df_csv.pivot_table(
            values='survived',
            index='sex',
            columns='pclass',
            aggfunc='mean'
        ).round(2)
        sns.heatmap(pivot, annot=True, fmt='.2f',
                    cmap='Blues', ax=ax)
        ax.set_title('Taxa de Sobrevivência: Sexo × Classe')

    st.pyplot(fig)