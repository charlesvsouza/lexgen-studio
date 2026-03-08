import os
import psycopg2
import psycopg2.errors
import sqlite3
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# Conexões
DATABASE_URL = os.getenv("DATABASE_URL")
LOCAL_DB = "lexgen_config_local.db" # Banco local APENAS para configurações do PC

def get_cloud_connection():
    """Gera conexão com o Supabase retornando dados como Dicionário"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def criar_tabelas():
    # 1. TABELA NA NUVEM (PostgreSQL) - Contas de Usuários
    if DATABASE_URL:
        with get_cloud_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        senha VARCHAR(255) NOT NULL,
                        plano VARCHAR(50) DEFAULT 'basic',
                        usos_ia INTEGER DEFAULT 0,
                        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            conn.commit()
    
    # 2. TABELA LOCAL (SQLite) - Configurações da máquina do advogado
    with sqlite3.connect(LOCAL_DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                id INTEGER PRIMARY KEY DEFAULT 1,
                escritorio TEXT,
                advogado TEXT,
                oab TEXT,
                pasta_padrao TEXT
            )
        """)
        conn.commit()

# ==========================================
# FUNÇÕES DE NUVEM (SUPABASE)
# ==========================================
def registrar_usuario(email, senha):
    try:
        with get_cloud_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO usuarios (email, senha) VALUES (%s, %s)",
                    (email, senha)
                )
            conn.commit()
        return True, "Conta criada com sucesso!"
    except psycopg2.errors.UniqueViolation:
        return False, "E-mail já está cadastrado no sistema."
    except Exception as e:
        return False, f"Erro no servidor: {e}"

def autenticar_usuario(email, senha):
    with get_cloud_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE email = %s AND senha = %s", (email, senha))
            return cursor.fetchone()

def obter_usuario(email):
    with get_cloud_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            return cursor.fetchone()

def registrar_uso_ia(email):
    with get_cloud_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE usuarios SET usos_ia = usos_ia + 1 WHERE email = %s", (email,))
        conn.commit()

def atualizar_plano_pro(email):
    with get_cloud_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE usuarios SET plano = 'pro' WHERE email = %s", (email,))
        conn.commit()

# ==========================================
# FUNÇÕES LOCAIS (SQLITE)
# ==========================================
def salvar_configuracoes(escritorio, advogado, oab, pasta):
    with sqlite3.connect(LOCAL_DB) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO configuracoes (id, escritorio, advogado, oab, pasta_padrao) 
            VALUES (1, ?, ?, ?, ?)
        """, (escritorio, advogado, oab, pasta))
        conn.commit()

def carregar_configuracoes():
    with sqlite3.connect(LOCAL_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT escritorio, advogado, oab, pasta_padrao FROM configuracoes WHERE id = 1")
        return cursor.fetchone()