# main.py (VERSÃO FINAL CONSOLIDADA com Detalhes do Pedido)
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from ttkthemes import ThemedTk
from db import inicializar_db, executar_comando
from forms.cliente_form import ClienteForm
from forms.produto_form import ProdutoForm
from forms.pedido_form import PedidoForm
# NOVO: Importa a classe para mostrar os detalhes
from forms.detalhes_pedido_form import DetalhesPedidoForm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class App(ThemedTk):
    def __init__(self):
        super().__init__(theme="arc")
        self.title("Sistema de Gestão de Clientes e Pedidos (Arc Theme)")
        self.geometry("900x650")

        inicializar_db()

        # Configuração da UI principal usando Notebook (Abas)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        self.setup_cliente_tab()
        self.setup_produto_tab()
        self.setup_pedido_tab()

        self.recarregar_clientes()
        self.recarregar_produtos()
        self.recarregar_pedidos()  # Inicializa a lista de pedidos

        # Adiciona evento para recarregar pedidos ao mudar para a aba de Pedidos
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

    def _on_tab_change(self, event):
        """Recarrega dados se a aba de Pedidos for selecionada."""
        tab_index = self.notebook.index("current")
        tab_name = self.notebook.tab(tab_index, "text")
        if tab_name == "Pedidos":
            self.recarregar_pedidos()

    # --- Métodos de Setup de Abas ---

    def setup_cliente_tab(self):
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Clientes")

        frame_busca = ttk.Frame(frame)
        frame_busca.pack(fill="x")
        ttk.Label(frame_busca, text="Buscar Cliente (Nome/Email):").pack(side="left", padx=5, pady=5)
        self.var_busca_cliente = tk.StringVar()
        self.entry_busca_cliente = ttk.Entry(frame_busca, textvariable=self.var_busca_cliente, width=50)
        self.entry_busca_cliente.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_busca_cliente.bind('<KeyRelease>', lambda e: self.recarregar_clientes())

        list_frame = ttk.Frame(frame)
        list_frame.pack(fill="both", expand=True, pady=5)
        self.tree_clientes = self._criar_treeview(list_frame, ("ID", "Nome", "Email", "Telefone"))
        self.tree_clientes.column("ID", width=50, anchor="center");
        self.tree_clientes.heading("ID", text="ID")
        self.tree_clientes.column("Nome", width=250);
        self.tree_clientes.heading("Nome", text="Nome")
        self.tree_clientes.column("Email", width=250);
        self.tree_clientes.heading("Email", text="Email")
        self.tree_clientes.column("Telefone", width=150);
        self.tree_clientes.heading("Telefone", text="Telefone")

        frame_botoes = ttk.Frame(frame, padding="5")
        frame_botoes.pack(fill="x")
        ttk.Button(frame_botoes, text="Novo Cliente", command=self.abrir_novo_cliente, style='Accent.TButton').pack(
            side="left", padx=5)
        ttk.Button(frame_botoes, text="Editar Cliente", command=self.abrir_editar_cliente).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Excluir Cliente", command=self.excluir_cliente, style='TButton').pack(
            side="left", padx=5)
        self.tree_clientes.bind('<Double-1>', lambda e: self.abrir_editar_cliente())

    def setup_produto_tab(self):
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Produtos")

        frame_busca = ttk.Frame(frame)
        frame_busca.pack(fill="x")
        ttk.Label(frame_busca, text="Buscar Produto (Nome):").pack(side="left", padx=5, pady=5)
        self.var_busca_produto = tk.StringVar()
        self.entry_busca_produto = ttk.Entry(frame_busca, textvariable=self.var_busca_produto, width=50)
        self.entry_busca_produto.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_busca_produto.bind('<KeyRelease>', lambda e: self.recarregar_produtos())

        list_frame = ttk.Frame(frame)
        list_frame.pack(fill="both", expand=True, pady=5)
        self.tree_produtos = self._criar_treeview(list_frame, ("ID", "Nome", "Preço", "Estoque"))
        self.tree_produtos.column("ID", width=50, anchor="center");
        self.tree_produtos.heading("ID", text="ID")
        self.tree_produtos.column("Nome", width=300);
        self.tree_produtos.heading("Nome", text="Nome")
        self.tree_produtos.column("Preço", width=150, anchor="e");
        self.tree_produtos.heading("Preço", text="Preço Unit. R$")
        self.tree_produtos.column("Estoque", width=100, anchor="center");
        self.tree_produtos.heading("Estoque", text="Estoque")

        frame_botoes = ttk.Frame(frame, padding="5")
        frame_botoes.pack(fill="x")
        ttk.Button(frame_botoes, text="Novo Produto", command=self.abrir_novo_produto, style='Accent.TButton').pack(
            side="left", padx=5)
        ttk.Button(frame_botoes, text="Editar Produto", command=self.abrir_editar_produto).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Excluir Produto", command=self.excluir_produto, style='TButton').pack(
            side="left", padx=5)
        self.tree_produtos.bind('<Double-1>', lambda e: self.abrir_editar_produto())

    # Setup da Aba de Pedidos (AGORA COM LISTAGEM E BINDING)
    def setup_pedido_tab(self):
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Pedidos")

        frame_busca = ttk.Frame(frame)
        frame_busca.pack(fill="x")
        ttk.Label(frame_busca, text="Lista de Pedidos (mais recentes primeiro)").pack(side="left", padx=5, pady=5)
        ttk.Button(frame_busca, text="Atualizar Lista", command=self.recarregar_pedidos).pack(side="right", padx=5)

        list_frame = ttk.Frame(frame)
        list_frame.pack(fill="both", expand=True, pady=5)

        self.tree_pedidos = self._criar_treeview(list_frame, ("ID", "Cliente", "Data", "Total"))
        self.tree_pedidos.column("ID", width=70, anchor="center");
        self.tree_pedidos.heading("ID", text="ID")
        self.tree_pedidos.column("Cliente", width=300);
        self.tree_pedidos.heading("Cliente", text="Cliente")
        self.tree_pedidos.column("Data", width=150, anchor="center");
        self.tree_pedidos.heading("Data", text="Data")
        self.tree_pedidos.column("Total", width=150, anchor="e");
        self.tree_pedidos.heading("Total", text="Total R$")

        # NOVO BINDING: Duplo clique abre os detalhes
        self.tree_pedidos.bind('<Double-1>', lambda e: self.abrir_detalhes_pedido())

        frame_botoes = ttk.Frame(frame, padding="5")
        frame_botoes.pack(fill="x")

        ttk.Button(frame_botoes, text="Novo Pedido", command=self.abrir_novo_pedido, style='Accent.TButton').pack(
            side="left", padx=5)
        # NOVO BOTÃO: Adicionado o botão "Ver Detalhes"
        ttk.Button(frame_botoes, text="Ver Detalhes", command=self.abrir_detalhes_pedido).pack(side="left", padx=5)

    def _criar_treeview(self, parent_frame, colunas):
        tree = ttk.Treeview(parent_frame, columns=colunas, show="headings")
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return tree

    # --- Métodos de Recarregamento de Dados ---

    def recarregar_clientes(self):
        self._recarregar_dados(self.tree_clientes, "clientes", self.var_busca_cliente.get().strip(),
                               "nome LIKE ? OR email LIKE ?",
                               "id, nome, email, telefone")

    def recarregar_produtos(self):
        self._recarregar_dados(self.tree_produtos, "produtos", self.var_busca_produto.get().strip(),
                               "nome LIKE ?",
                               "id, nome, preco, estoque")

    def recarregar_pedidos(self):
        """Busca pedidos no DB e recarrega a Treeview de pedidos (Lógica de Inserção Corrigida)."""
        for item in self.tree_pedidos.get_children():
            self.tree_pedidos.delete(item)

        sql = """
            SELECT 
                p.id, 
                c.nome, 
                p.data, 
                p.total 
            FROM pedidos p
            INNER JOIN clientes c ON p.cliente_id = c.id
            ORDER BY p.data DESC, p.id DESC
        """
        try:
            pedidos = executar_comando(sql, fetchall=True)
            if pedidos:
                for pedido in pedidos:
                    # pedido é: (id, nome_cliente, data, total)
                    pedido_id = pedido[0]
                    nome_cliente = pedido[1]
                    data = pedido[2]
                    total_formatado = f"{pedido[3]:.2f}"

                    # INSERÇÃO CORRETA: Garante a ordem dos dados na Treeview
                    self.tree_pedidos.insert(
                        "",
                        "end",
                        iid=pedido_id,
                        values=(pedido_id, nome_cliente, data, total_formatado)
                    )
            else:
                self.tree_pedidos.insert("", "end", values=("", "Nenhum pedido encontrado.", "", ""), tags=('empty',))
        except Exception as e:
            logging.error(f"Erro ao carregar pedidos: {e}")
            messagebox.showerror("Erro de DB", f"Não foi possível carregar a lista de pedidos: {e}")

    def _recarregar_dados(self, treeview, tabela, termo, where_clause, colunas_sql):
        # Limpa o Treeview
        for item in treeview.get_children():
            treeview.delete(item)

        sql = f"SELECT {colunas_sql} FROM {tabela}"
        parametros = ()

        if termo:
            sql += f" WHERE {where_clause}"
            if tabela == "clientes":
                parametros = (f'%{termo}%', f'%{termo}%')
            elif tabela == "produtos":
                parametros = (f'%{termo}%',)  # Apenas busca por nome

        try:
            dados = executar_comando(sql, parametros, fetchall=True)
            if dados:
                for dado in dados:
                    # Formata o preço para exibição no Treeview de Produtos
                    if tabela == "produtos":
                        dado_list = list(dado)
                        dado_list[2] = f"{dado_list[2]:.2f}"
                        treeview.insert("", "end", iid=dado_list[0], values=dado_list)
                    else:
                        treeview.insert("", "end", iid=dado[0], values=dado)

        except Exception as e:
            logging.error(f"Erro ao carregar dados de {tabela}: {e}")
            messagebox.showerror("Erro de DB", f"Não foi possível carregar a lista de {tabela}: {e}")

    # --- Métodos CRUD de Clientes e Produtos (permanecem os mesmos) ---

    def _get_selected_id(self, treeview):
        selecionado = treeview.selection()
        if not selecionado:
            messagebox.showwarning("Seleção", "Selecione um item na lista.")
            return None
        return selecionado[0]

    def abrir_novo_cliente(self):
        ClienteForm(self, recarregar_callback=self.recarregar_clientes)

    def abrir_editar_cliente(self):
        cliente_id = self._get_selected_id(self.tree_clientes)
        if cliente_id:
            ClienteForm(self, cliente_id=int(cliente_id), recarregar_callback=self.recarregar_clientes)

    def excluir_cliente(self):
        cliente_id = self._get_selected_id(self.tree_clientes)
        if cliente_id:
            if messagebox.askyesno("Confirmar Exclusão",
                                   "Tem certeza que deseja excluir o cliente selecionado? "
                                   "Todos os pedidos associados serão EXCLUÍDOS (CASCADE)."):
                try:
                    executar_comando("DELETE FROM clientes WHERE id = ?", (cliente_id,))
                    messagebox.showinfo("Sucesso", "Cliente excluído!")
                    self.recarregar_clientes()
                except Exception as e:
                    logging.error(f"Erro ao excluir cliente: {e}")
                    messagebox.showerror("Erro de DB", f"Não foi possível excluir o cliente: {e}")

    def abrir_novo_produto(self):
        ProdutoForm(self, recarregar_callback=self.recarregar_produtos)

    def abrir_editar_produto(self):
        produto_id = self._get_selected_id(self.tree_produtos)
        if produto_id:
            ProdutoForm(self, produto_id=int(produto_id), recarregar_callback=self.recarregar_produtos)

    def excluir_produto(self):
        produto_id = self._get_selected_id(self.tree_produtos)
        if produto_id:
            if messagebox.askyesno("Confirmar Exclusão",
                                   "Tem certeza que deseja excluir o produto selecionado? "
                                   "Pedidos que o contêm serão afetados (o item permanecerá com o nome, mas sem link)."):
                try:
                    executar_comando("DELETE FROM produtos WHERE id = ?", (produto_id,))
                    messagebox.showinfo("Sucesso", "Produto excluído!")
                    self.recarregar_produtos()
                except Exception as e:
                    logging.error(f"Erro ao excluir produto: {e}")
                    messagebox.showerror("Erro de DB", f"Não foi possível excluir o produto: {e}")

    # --- Métodos de Pedidos ---
    def abrir_novo_pedido(self):
        def callback_completo():
            self.recarregar_pedidos()
            self.recarregar_produtos()

        PedidoForm(self, recarregar_callback=callback_completo)

    def abrir_detalhes_pedido(self):
        """Abre a janela de detalhes para o pedido selecionado."""
        pedido_id = self._get_selected_id(self.tree_pedidos)
        if pedido_id:
            try:
                # Converte o ID para int
                DetalhesPedidoForm(self, pedido_id=int(pedido_id))
            except ValueError:
                messagebox.showerror("Erro", "ID de pedido inválido.")


if __name__ == "__main__":
    app = App()
    app.mainloop()