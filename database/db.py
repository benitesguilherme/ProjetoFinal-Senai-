"""
Módulo de Acesso e Gerenciamento do Banco de Dados SQLite
CineSENAI & Teatro
"""

import os
import sqlite3
from database.seed import init_db, DB_PATH, SCHEMA_PATH

def get_db():
    """Retorna uma conexão ativa configurada para o banco SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def check_and_init_db():
    """Garante que o banco de dados e as tabelas estejam criados ao iniciar o app."""
    if not os.path.exists(DB_PATH):
        print(f"Banco de dados não encontrado em {DB_PATH}. Inicializando schema e seed...")
        init_db(force_recreate=True)
    else:
        # Testa se a tabela eventos existe e tem registros
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM eventos")
            count = cursor.fetchone()[0]
            conn.close()
            if count == 0:
                print("Banco existente vazio. Aplicando seed sem remover o arquivo...")
                init_db(force_recreate=False)
        except Exception as e:
            raise RuntimeError("Não foi possível abrir o banco. O arquivo foi preservado; verifique a conexão e o schema.") from e
