import sqlite3

DB_NAME = "assinaturas.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def criar_tabela():
    with conectar() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS assinaturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                servico TEXT NOT NULL,
                categoria TEXT NOT NULL,
                valor REAL NOT NULL,
                dia_cobranca INTEGER NOT NULL,
                site TEXT
            )
        """)
        # Garante compatibilidade caso a tabela antiga não tenha a coluna site
        try:
            conn.execute("ALTER TABLE assinaturas ADD COLUMN site TEXT")
        except sqlite3.OperationalError:
            pass

def adicionar_assinatura(servico, categoria, valor, dia_cobranca, site=""):
    with conectar() as conn:
        conn.execute(
            "INSERT INTO assinaturas (servico, categoria, valor, dia_cobranca, site) VALUES (?, ?, ?, ?, ?)",
            (servico, categoria, valor, dia_cobranca, site)
        )

def listar_assinaturas():
    with conectar() as conn:
        cursor = conn.execute("SELECT id, servico, categoria, valor, dia_cobranca, site FROM assinaturas ORDER BY dia_cobranca")
        return cursor.fetchall()

def deletar_assinatura(id_assinatura):
    with conectar() as conn:
        conn.execute("DELETE FROM assinaturas WHERE id = ?", (id_assinatura,))