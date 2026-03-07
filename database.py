import sqlite3

DB_NAME = "lexgen_dados.db"

def criar_tabelas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabela do Escritório
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes_escritorio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_escritorio TEXT NOT NULL,
            oab TEXT
        )
    ''')
    
    # Migração do Escritório
    cursor.execute("PRAGMA table_info(configuracoes_escritorio)")
    colunas_esc = [col[1] for col in cursor.fetchall()]
    if "pasta_salvamento" not in colunas_esc:
        cursor.execute("ALTER TABLE configuracoes_escritorio ADD COLUMN pasta_salvamento TEXT")
    if "nome_advogado" not in colunas_esc:
        cursor.execute("ALTER TABLE configuracoes_escritorio ADD COLUMN nome_advogado TEXT")
        
    # NOVA Tabela de Usuários (SaaS)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            plano TEXT DEFAULT 'basic',
            usos_ia INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

# --- FUNÇÕES DE USUÁRIO (SAAS) ---

def registrar_usuario(email, senha):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (email, senha, plano, usos_ia) VALUES (?, ?, 'basic', 0)", (email, senha))
        conn.commit()
        conn.close()
        return True, "Usuário registrado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "E-mail já cadastrado!"
    except Exception as e:
        return False, f"Erro: {str(e)}"

def autenticar_usuario(email, senha):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, plano, usos_ia FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {"id": row[0], "email": row[1], "plano": row[2], "usos_ia": row[3]}
    return None

def obter_usuario(email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, plano, usos_ia FROM usuarios WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "email": row[1], "plano": row[2], "usos_ia": row[3]}
    return None

def registrar_uso_ia(email):
    """Incrementa o contador de uso da IA do usuário logado"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET usos_ia = usos_ia + 1 WHERE email = ?", (email,))
    conn.commit()
    conn.close()

def atualizar_plano_pro(email):
    """Muda o plano do usuário para PRO e zera o contador"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET plano = 'pro' WHERE email = ?", (email,))
    conn.commit()
    conn.close()

# --- FUNÇÕES DE CONFIGURAÇÃO DO ESCRITÓRIO ---

def salvar_configuracoes(nome_escritorio, nome_advogado, oab, pasta_salvamento):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM configuracoes_escritorio")
    cursor.execute("INSERT INTO configuracoes_escritorio (nome_escritorio, nome_advogado, oab, pasta_salvamento) VALUES (?, ?, ?, ?)", (nome_escritorio, nome_advogado, oab, pasta_salvamento))
    conn.commit()
    conn.close()

def carregar_configuracoes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT nome_escritorio, nome_advogado, oab, pasta_salvamento FROM configuracoes_escritorio LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row