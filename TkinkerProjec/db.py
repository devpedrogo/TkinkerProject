import sqlite3
from datetime import datetime
import logging

# Configuração de logging simples para registrar erros de DB
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Nome do arquivo do banco de dados
DB_FILE = 'gerenciador_pedidos.db'


def inicializar_banco():
    """
    Cria a conexão com o banco de dados e as tabelas (clientes, pedidos, itens_pedido)
    se elas ainda não existirem.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Tabela Clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT UNIQUE,
                telefone TEXT
            );
        """)

        # Tabela Pedidos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY,
                cliente_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
            );
        """)

        # Tabela Itens do Pedido
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_pedido (
                id INTEGER PRIMARY KEY,
                pedido_id INTEGER NOT NULL,
                produto TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unit REAL NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
            );
        """)

        conn.commit()
        logging.info("Banco de dados inicializado com sucesso.")

    except sqlite3.Error as e:
        logging.error(f"Erro ao inicializar o banco de dados: {e}")
        # Lança o erro para que o aplicativo possa tratar a falha crítica
        raise
    finally:
        if conn:
            conn.close()


def executar_comando(sql, parametros=(), fetchone=False, fetchall=False, transactional=False):
    """
    Executa um comando SQL parametrizado de forma segura e com tratamento de erros.

    Args:
        sql (str): A string do comando SQL (ex: INSERT, UPDATE, DELETE, SELECT).
        parametros (tuple): Uma tupla com os valores para os placeholders (?).
        fetchone (bool): Se True, retorna a primeira linha do resultado.
        fetchall (bool): Se True, retorna todas as linhas do resultado.
        transactional (bool): Se True, a transação é deixada em aberto (não é dado commit/close)
                              para ser usada em operações multi-passo (como inserção de Pedido).

    Returns:
        Um único resultado, uma lista de resultados, ou None.
    """
    conn = None
    resultado = None

    try:
        # Conecta ao banco de dados e habilita chaves estrangeiras
        conn = sqlite3.connect(DB_FILE)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        # Executa o comando
        cursor.execute(sql, parametros)

        # Trata as requisições de SELECT
        if fetchone:
            resultado = cursor.fetchone()
        elif fetchall:
            resultado = cursor.fetchall()

        # Para comandos que alteram dados, confirma a transação
        if sql.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')) and not transactional:
            conn.commit()

        # Se for um INSERT, tenta retornar o ID da última linha inserida
        if sql.strip().upper().startswith('INSERT') and not fetchone and not fetchall:
            # Retorna o ID da nova linha inserida, útil para obter o 'id' do Cliente ou Pedido
            resultado = cursor.lastrowid

    except sqlite3.Error as e:
        # Em caso de erro, desfaz a transação e registra o erro
        if conn:
            conn.rollback()
        logging.error(f"Erro no comando SQL: {e}")
        logging.error(f"SQL: {sql}, Params: {parametros}")
        # Lança o erro para que a interface possa tratá-lo e notificar o usuário
        raise

    finally:
        # Fecha a conexão, exceto se for uma transação em aberto
        if conn and not transactional:
            conn.close()

    return resultado


# Opcionalmente, adicione um helper para transações complexas (será útil no Prompt 4)
def iniciar_transacao():
    """Retorna uma conexão aberta para operações transacionais."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Erro ao iniciar transação: {e}")
        raise


if __name__ == '__main__':
    # Bloco de teste: inicializa o banco de dados e insere um cliente de exemplo
    try:
        inicializar_banco()

        # Teste de inserção
        print("--- Teste de Inserção de Cliente ---")
        nome = "Ana Silva"
        email = "ana.s@exemplo.com"
        telefone = "551199998888"
        insert_sql = "INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)"
        cliente_id = executar_comando(insert_sql, (nome, email, telefone))
        print(f"Cliente inserido com ID: {cliente_id}")

        # Teste de seleção
        print("--- Teste de Seleção de Cliente ---")
        select_sql = "SELECT id, nome, email, telefone FROM clientes WHERE id = ?"
        cliente = executar_comando(select_sql, (cliente_id,), fetchone=True)
        print(f"Cliente recuperado: {cliente}")

    except Exception as e:
        print(f"Ocorreu um erro durante o teste do DB: {e}")