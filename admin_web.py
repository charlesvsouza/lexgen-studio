import streamlit as st
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

# Carrega a mesma string de conexão do seu .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

st.set_page_config(page_title="Admin - LexGen", page_icon="⚖️", layout="wide")

st.title("⚖️ LexGen Studio - Painel Administrativo")
st.markdown("Bem-vindo ao controle de usuários do seu SaaS.")

@st.cache_data(ttl=60) # Atualiza os dados a cada 60 segundos
def carregar_usuarios():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        # Usamos Pandas para criar uma tabela linda automaticamente!
        df = pd.read_sql_query("SELECT id, email, plano, usos_ia, criado_em FROM usuarios", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao conectar no banco: {e}")
        return pd.DataFrame()

df_usuarios = carregar_usuarios()

if not df_usuarios.empty:
    # Cria os cards com os números do seu negócio
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Advogados", len(df_usuarios))
    col2.metric("Assinantes PRO", len(df_usuarios[df_usuarios['plano'] == 'pro']))
    col3.metric("Uso de IA (Total)", df_usuarios['usos_ia'].sum())

    st.subheader("📋 Lista de Clientes")
    st.dataframe(df_usuarios, use_container_width=True, hide_index=True)
else:
    st.info("Nenhum usuário cadastrado ainda ou aguardando conexão...")