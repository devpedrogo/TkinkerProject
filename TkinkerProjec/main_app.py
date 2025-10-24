import tkinter as tk
from tkinter import ttk, messagebox
import logging

# Importa as classes e funções necessárias
try:
    from db import inicializar_banco, executar_comando
    from cliente_form import ClienteForm
except ImportError:
    logging.error("Certifique-se de que db.py e cliente_form.py estão no mesmo diretório.")
    # Saída do aplicativo se a importação falhar
    raise SystemExit


class GerenciadorPedidosApp(tk.Tk):
    """
    Classe principal do aplicativo Tkinter.
    """

    def __init__(self):
        super().__init__()
        self.title("Gerenciador de Pedidos e Clientes")
        self.geometry("800x600")

        # Inicializa o banco de dados
        try:
            inicializar_banco()
        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Falha ao iniciar o banco de dados: {e}")
            self.destroy()  # Fecha a janela se o DB não iniciar
            return

        self.criar_interface_clientes()
        self.recarregar_lista_clientes()  # Carrega os dados na inicialização

    def criar_interface_clientes(self):
        """Cria o frame de gestão de clientes (lista, busca e botões)."""

        # Frame principal para a seção de Clientes
        clientes_frame = ttk.Frame(self, padding="10")
        clientes_frame.pack(fill="both", expand=True)

        # ------------------- TÍTULO -------------------
        tk.Label(clientes_frame, text="Gestão de Clientes", font=('Arial', 16, 'bold'), anchor="w").pack(fill="x",
                                                                                                         pady=(0, 10))

        # ------------------- BARRA DE BUSCA -------------------
        busca_frame = ttk.Frame(clientes_frame)
        busca_frame.pack(fill="x", pady=5)

        tk.Label(busca_frame, text="Buscar Cliente:").pack(side="left", padx=5)
        self.busca_var = tk.StringVar()
        self.busca_entry = ttk.Entry(busca_frame, textvariable=self.busca_var, width=50)
        self.busca_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Configura o callback para buscar ao digitar e ao pressionar Enter
        self.busca_var.trace_add("write", lambda *args: self.recarregar_lista_clientes())
        self.busca_entry.bind("<Return>", lambda e: self.recarregar_lista_clientes())

        # ------------------- TREEVIEW (LISTA DE CLIENTES) -------------------
        self.tree = ttk.Treeview(clientes_frame,
                                 columns=("ID", "Nome", "Email", "Telefone"),
                                 show="headings")

        # Configuração das colunas
        self.tree.heading("ID", text="ID", anchor=tk.CENTER)
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Email", text="E-mail")
        self.tree.heading("Telefone", text="Telefone")

        # Tamanho das colunas
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Nome", width=250)
        self.tree.column("Email", width=200)
        self.tree.column("Telefone", width=150)

        # Adiciona barra de rolagem
        scrollbar = ttk.Scrollbar(clientes_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(fill="both", expand=True, pady=10, side="left")
        scrollbar.pack(fill="y", side="right")

        # Adiciona evento de duplo clique para edição
        self.tree.bind("<Double-1>", self._on_editar_cliente)

        # ------------------- BOTÕES DE AÇÃO -------------------
        botoes_frame = ttk.Frame(clientes_frame)
        botoes_frame.pack(fill="x", pady=10)

        ttk.Button(botoes_frame, text="Novo Cliente", command=self._on_novo_cliente).pack(side="left", padx=5)
        ttk.Button(botoes_frame, text="Editar Cliente", command=self._on_editar_cliente).pack(side="left", padx=5)
        ttk.Button(botoes_frame, text="Excluir Cliente", command=self._on_excluir_cliente).pack(side="left", padx=5)

    def recarregar_lista_clientes(self):
        """Busca os clientes no DB e preenche o Treeview, aplicando o filtro de busca."""
        try:
            # Limpa o Treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            termo_busca = self.busca_var.get().strip()

            if termo_busca:
                # Se houver termo, busca por nome OU email
                sql = "SELECT id, nome, email, telefone FROM clientes WHERE nome LIKE ? OR email LIKE ? ORDER BY nome"
                param = (f'%{termo_busca}%', f'%{termo_busca}%')
            else:
                # Caso contrário, busca todos
                sql = "SELECT id, nome, email, telefone FROM clientes ORDER BY nome"
                param = ()

            clientes = executar_comando(sql, param, fetchall=True)

            # Insere os dados no Treeview
            for cliente in clientes:
                # O Treeview espera uma lista ou tupla para cada linha
                self.tree.insert('', tk.END, values=cliente)

        except Exception as e:
            logging.error(f"Erro ao recarregar lista de clientes: {e}")
            messagebox.showerror("Erro de DB", "Não foi possível carregar a lista de clientes.")

    # ------------------- CALLBACKS DOS BOTÕES -------------------

    def _get_selected_cliente_id(self):
        """Retorna o ID do cliente selecionado no Treeview ou None."""
        item_selecionado = self.tree.focus()
        if not item_selecionado:
            messagebox.showwarning("Seleção", "Selecione um cliente na lista primeiro.")
            return None
        # O ID é o primeiro valor na tupla de valores do Treeview
        return self.tree.item(item_selecionado, 'values')[0]

    def _on_novo_cliente(self):
        """Abre o formulário para cadastro de um novo cliente."""
        # ClienteForm(master, cliente_id=None, callback_salvar=self.recarregar_lista_clientes)
        ClienteForm(self, callback_salvar=self.recarregar_lista_clientes)

    def _on_editar_cliente(self, event=None):
        """Abre o formulário para edição do cliente selecionado."""
        cliente_id = self._get_selected_cliente_id()
        if cliente_id is not None:
            # ClienteForm(master, cliente_id=ID, callback_salvar=self.recarregar_lista_clientes)
            ClienteForm(self, cliente_id=cliente_id, callback_salvar=self.recarregar_lista_clientes)

    def _on_excluir_cliente(self):
        """Exclui o cliente selecionado após confirmação."""
        cliente_id = self._get_selected_cliente_id()
        if cliente_id is None:
            return

        # Busca o nome do cliente para a mensagem de confirmação
        try:
            sql_nome = "SELECT nome FROM clientes WHERE id = ?"
            nome_cliente = executar_comando(sql_nome, (cliente_id,), fetchone=True)[0]
        except Exception:
            nome_cliente = f"Cliente ID {cliente_id}"

        # Pede confirmação (UX)
        confirmar = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja EXCLUIR o cliente '{nome_cliente}'?\n"
            "Todos os pedidos relacionados também serão excluídos!",  # Alerta sobre CASCADE DELETE
            parent=self
        )

        if confirmar:
            try:
                sql_delete = "DELETE FROM clientes WHERE id = ?"
                executar_comando(sql_delete, (cliente_id,))
                messagebox.showinfo("Sucesso", f"Cliente '{nome_cliente}' excluído com sucesso.")
                self.recarregar_lista_clientes()  # Recarrega a lista
            except Exception as e:
                logging.error(f"Erro ao excluir cliente ID {cliente_id}: {e}")
                messagebox.showerror("Erro de DB", "Não foi possível excluir o cliente.")


if __name__ == '__main__':
    app = GerenciadorPedidosApp()
    app.mainloop()