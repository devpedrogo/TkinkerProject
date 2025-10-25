# db.py (ALTERADO)
import sqlite3
from sqlite3 import Error
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_NAME = "pedidos.db"


# ... (criar_conexao permanece o mesmo)

def criar_conexao(db_file=DATABASE_NAME):
    """Cria uma conexão com o banco de dados SQLite especificado."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except Error as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        if conn:
            conn.close()
        return None


def inicializar_db():
    """Cria as tabelas do esquema, incluindo a nova tabela 'produtos'."""
    conn = criar_conexao()
    if conn is not None:
        try:
            cursor = conn.cursor()

            # Garante que chaves estrangeiras estão ligadas
            cursor.execute("PRAGMA foreign_keys = ON;")

            # Tabela CLIENTES
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT UNIQUE,
                    telefone TEXT
                );
            """)

            # Tabela PRODUTOS
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL,
                    preco REAL NOT NULL,
                    estoque INTEGER NOT NULL DEFAULT 0
                );
            """)

            # Tabela PEDIDOS
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pedidos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER NOT NULL,
                    data TEXT NOT NULL,
                    total REAL NOT NULL,
                    FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE
                );
            """)

            # Tabela ITENS_PEDIDO
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS itens_pedido (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pedido_id INTEGER NOT NULL,
                    produto_id INTEGER,
                    produto_nome TEXT NOT NULL,
                    quantidade INTEGER NOT NULL,
                    preco_unit REAL NOT NULL,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos (id) ON DELETE CASCADE,
                    FOREIGN KEY (produto_id) REFERENCES produtos (id) ON DELETE SET NULL
                );
            """)
            conn.commit()
            logging.info("Banco de dados inicializado com sucesso.")
        except Error as e:
            logging.error(f"Erro ao criar tabelas: {e}")
            # Adicione esta linha para ver o erro no console
            print(f"ERRO CRÍTICO NA CRIAÇÃO DE TABELAS: {e}")
        finally:
            conn.close()
    else:
        logging.error("Não foi possível estabelecer a conexão para inicialização do DB.")


# ... (executar_comando permanece o mesmo)

def executar_comando(sql, parametros=(), fetchone=False, fetchall=False, commit=True):
    """
    Executa comandos SQL (SELECT, INSERT, UPDATE, DELETE) parametrizados.

    Retorna o resultado da consulta (se fetchone/fetchall for True),
    ou o ID da última linha inserida (se for INSERT), ou None.
    """
    conn = criar_conexao()
    resultado = None
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute(sql, parametros)

        if fetchone:
            resultado = cursor.fetchone()
        elif fetchall:
            resultado = cursor.fetchall()
        elif commit:
            conn.commit()
            if sql.strip().upper().startswith("INSERT"):
                resultado = cursor.lastrowid

    except sqlite3.IntegrityError as e:
        # Tratamento específico para erros de integridade (ex: UNIQUE)
        logging.warning(f"Erro de Integridade no DB: {e}. SQL: {sql}")
        resultado = "IntegrityError"
        if commit: conn.rollback()
    except Error as e:
        logging.error(f"Erro ao executar comando SQL: {e}. SQL: {sql} - Params: {parametros}")
        if commit: conn.rollback()
    finally:
        if conn:
            conn.close()
    return resultado