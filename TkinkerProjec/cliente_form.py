import tkinter as tk
from tkinter import Toplevel, Label, Entry, Button, messagebox
import re
import logging

# Importa as funções do banco de dados (assumindo que db.py está no mesmo diretório)
try:
    from db import executar_comando
except ImportError:
    logging.error("O arquivo db.py não foi encontrado. Certifique-se de que ele está no mesmo diretório.")
    executar_comando = None  # Define como None para evitar erros na classe, mas o app não funcionará.


class ClienteForm(Toplevel):
    """
    Janela Toplevel para cadastrar ou editar um cliente.
    """

    def __init__(self, master, cliente_id=None, callback_salvar=None):
        super().__init__(master)
        self.master = master
        self.cliente_id = cliente_id
        self.callback_salvar = callback_salvar  # Função a ser chamada após salvar/editar

        # Configurações básicas da janela
        self.title("Cadastrar Cliente" if cliente_id is None else "Editar Cliente")
        self.geometry("400x250")
        self.resizable(False, False)

        # Variáveis de controle para os campos do formulário
        self.var_nome = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_telefone = tk.StringVar()

        # Variável para rastrear se houve modificação de dados (para UX)
        self._modificado = False

        self.criar_widgets()

        # Se for edição, carrega os dados
        if self.cliente_id is not None:
            self._carregar_dados_cliente()

        # Adiciona tratamento para fechar a janela
        self.protocol("WM_DELETE_WINDOW", self._on_fechar)

        # Configura o rastreamento de modificações (UX)
        self.var_nome.trace_add("write", lambda *args: self._set_modificado(True))
        self.var_email.trace_add("write", lambda *args: self._set_modificado(True))
        self.var_telefone.trace_add("write", lambda *args: self._set_modificado(True))

    def _set_modificado(self, valor):
        """Define o estado de modificação e desabilita temporariamente o rastreamento."""
        if self._modificado != valor:
            self._modificado = valor

    def _carregar_dados_cliente(self):
        """Busca e preenche os dados do cliente para edição."""
        try:
            sql = "SELECT nome, email, telefone FROM clientes WHERE id = ?"
            dados = executar_comando(sql, (self.cliente_id,), fetchone=True)

            if dados:
                self.var_nome.set(dados[0])
                self.var_email.set(dados[1])
                self.var_telefone.set(dados[2] or "")  # Trata caso o telefone seja NULL
                self._set_modificado(False)  # Reseta o flag após carregar
            else:
                messagebox.showerror("Erro de Carregamento", "Cliente não encontrado.")
                self.destroy()

        except Exception as e:
            logging.error(f"Erro ao carregar cliente ID {self.cliente_id}: {e}")
            messagebox.showerror("Erro de DB", "Não foi possível carregar os dados do cliente.")
            self.destroy()

    def criar_widgets(self):
        """Cria e organiza os widgets do formulário."""

        # Frame principal com padding
        main_frame = tk.Frame(self, padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)

        # Campos do Formulário
        fields = [
            ("Nome:", self.var_nome),
            ("E-mail:", self.var_email),
            ("Telefone:", self.var_telefone)
        ]

        for i, (label_text, var) in enumerate(fields):
            label = Label(main_frame, text=label_text, anchor="w")
            label.grid(row=i, column=0, padx=5, pady=5, sticky="w")

            entry = Entry(main_frame, textvariable=var, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            # Adiciona a referência ao Entry para feedback de erro
            if label_text == "Nome:":
                self.entry_nome = entry
            elif label_text == "E-mail:":
                self.entry_email = entry
            elif label_text == "Telefone:":
                self.entry_telefone = entry

        # Frame para botões
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=15)

        # Botão Salvar
        btn_salvar = Button(button_frame, text="Salvar", command=self._on_salvar, bg="#4CAF50", fg="white",
                            relief="raised", padx=10)
        btn_salvar.pack(side="left", padx=10)

        # Botão Cancelar
        btn_cancelar = Button(button_frame, text="Cancelar", command=self._on_cancelar, bg="#f44336", fg="white",
                              relief="raised", padx=10)
        btn_cancelar.pack(side="left", padx=10)

        # Configura o grid para expandir a coluna dos campos
        main_frame.grid_columnconfigure(1, weight=1)

    def _validar_campos(self):
        """Executa todas as validações de campos e retorna True se forem válidas."""
        nome = self.var_nome.get().strip()
        email = self.var_email.get().strip()
        telefone = self.var_telefone.get().strip()

        erros = []

        # 1. Validação de Nome (Obrigatório)
        if not nome:
            erros.append(("Nome é obrigatório.", self.entry_nome))

        # 2. Validação de E-mail (Formato Simples)
        # O e-mail não é obrigatório (pode ser deixado em branco, mas se preenchido, deve ser válido)
        if email:
            # Regex simples que verifica padrão algo@algo.algo
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                erros.append(("E-mail inválido.", self.entry_email))

        # 3. Validação de Telefone (8 a 15 dígitos)
        # O telefone não é obrigatório (pode ser deixado em branco, mas se preenchido, deve ser válido)
        if telefone:
            # Remove caracteres não numéricos para validação de tamanho
            telefone_limpo = re.sub(r'\D', '', telefone)
            if not 8 <= len(telefone_limpo) <= 15:
                erros.append(("Telefone deve ter entre 8 e 15 dígitos.", self.entry_telefone))

        # Feedback e Resultado
        if erros:
            # Exibe o primeiro erro encontrado e foca no campo
            mensagem = erros[0][0]
            campo = erros[0][1]
            messagebox.showwarning("Validação", mensagem)
            campo.focus_set()
            # Opcionalmente, pode-se mudar a cor do campo com erro:
            campo.config(bg="#FFDDDD")
            # Adiciona um evento para resetar a cor ao digitar:
            campo.bind("<Key>", lambda e, c=campo: c.config(bg="white"))
            return False
        else:
            # Se não houver erros, garante que todas as cores de fundo estão normais
            self.entry_nome.config(bg="white")
            self.entry_email.config(bg="white")
            self.entry_telefone.config(bg="white")
            return True

    def _on_salvar(self):
        """Callback acionado pelo botão Salvar."""
        if not executar_comando:
            messagebox.showerror("Erro", "O módulo de banco de dados não foi carregado corretamente.")
            return

        if not self._validar_campos():
            return

        nome = self.var_nome.get().strip()
        email = self.var_email.get().strip() or None  # Salva como NULL se vazio
        telefone = self.var_telefone.get().strip() or None  # Salva como NULL se vazio

        try:
            if self.cliente_id is None:
                # Inserção de novo cliente
                sql = "INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)"
                executar_comando(sql, (nome, email, telefone))
                messagebox.showinfo("Sucesso", f"Cliente '{nome}' cadastrado com sucesso!")
            else:
                # Atualização de cliente existente
                sql = "UPDATE clientes SET nome = ?, email = ?, telefone = ? WHERE id = ?"
                executar_comando(sql, (nome, email, telefone, self.cliente_id))
                messagebox.showinfo("Sucesso", f"Cliente '{nome}' atualizado com sucesso!")

            # Chama o callback para atualizar a lista principal
            if self.callback_salvar:
                self.callback_salvar()

            self._set_modificado(False)  # Resetar flag
            self.destroy()  # Fecha a janela após o sucesso

        except Exception as e:
            # Trata erro de DB, como violação de UNIQUE (e-mail já cadastrado)
            logging.error(f"Erro ao salvar cliente: {e}")
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Erro de DB", "O E-mail fornecido já está cadastrado para outro cliente.")
                self.entry_email.focus_set()
                self.entry_email.config(bg="#FFDDDD")
            else:
                messagebox.showerror("Erro de DB", "Ocorreu um erro ao salvar os dados.")

    def _on_cancelar(self):
        """Callback acionado pelo botão Cancelar e pelo X da janela."""
        self._on_fechar()

    def _on_fechar(self):
        """Verifica dados não salvos antes de fechar (UX)."""
        if self._modificado:
            resposta = messagebox.askyesno(
                "Dados Não Salvos",
                "Existem dados não salvos. Deseja descartar e fechar o formulário?",
                parent=self
            )
            if resposta:
                self.destroy()
        else:
            self.destroy()


# Exemplo de como a classe seria usada (apenas para testar o formulário isoladamente)
if __name__ == '__main__':
    # O bloco de teste abaixo só funcionará se o db.py estiver corretamente configurado
    # e inicializado.

    # Simula o inicializador do banco antes de rodar a aplicação
    try:
        from db import inicializar_banco

        inicializar_banco()
    except Exception as e:
        print(f"Erro ao inicializar DB para teste: {e}")

    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal


    def cliente_salvo():
        print("Cliente salvo! Recarregar lista...")


    # Abre a janela de cadastro (ID None)
    form_cadastro = ClienteForm(root, cliente_id=None, callback_salvar=cliente_salvo)

    # Abre a janela de edição (simula a tentativa de editar o ID 1)
    # form_edicao = ClienteForm(root, cliente_id=1, callback_salvar=cliente_salvo)

    root.mainloop()
