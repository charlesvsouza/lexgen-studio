import streamlit as st
import pandas as pd
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Pegando as credenciais REST do Supabase (vamos precisar da URL e da KEY)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

st.set_page_config(page_title="Admin - LexGen", page_icon="⚖️", layout="wide")

st.title("⚖️ LexGen Studio - Painel Administrativo")
st.markdown("Bem-vindo ao controle de usuários do seu SaaS.")

@st.cache_data(ttl=60)
def carregar_usuarios():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table('usuarios').select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Aguardando configuração das variáveis no painel do Streamlit...")
        return pd.DataFrame()

df_usuarios = carregar_usuarios()

if not df_usuarios.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Advogados", len(df_usuarios))
    col2.metric("Assinantes PRO", len(df_usuarios[df_usuarios['plano'] == 'pro']))
    col3.metric("Uso de IA (Total)", df_usuarios['usos_ia'].sum())

    st.subheader("📋 Lista de Clientes")
    st.dataframe(df_usuarios, use_container_width=True, hide_index=True)
else:
    st.info("Painel aguardando variáveis de ambiente ou nenhum usuário cadastrado.")