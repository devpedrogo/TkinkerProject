📦 Gerenciador de Clientes e Pedidos (Tkinter & SQLite)

Este é um projeto de aplicação desktop desenvolvido em Python (Tkinter), focado na gestão básica de clientes e no registro transacional de pedidos com seus respectivos itens. Utiliza SQLite como banco de dados local para persistência de dados e implementa boas práticas de UX, validações e manipulação de transações.

✨ Funcionalidades Principais

O sistema foi construído em torno de dois módulos principais: Clientes e Pedidos.

👥 Gestão de Clientes

CRUD Completo: Criação, visualização, edição e exclusão de clientes.

Validações Robustas: Validação de campos obrigatórios (nome), formato simples de e-mail e faixa de dígitos para telefone (8 a 15).

Busca Dinâmica: Filtro de clientes por nome ou e-mail na tela principal.

🧾 Gestão de Pedidos (Transacional)

Criação Transacional: Salva o pedido principal e todos os seus itens (cabeçalho e detalhes) em uma única transação, garantindo a integridade dos dados (commit/rollback).

Gerenciamento de Itens: Interface dedicada para adicionar e remover itens (produto, quantidade, preço unitário) do pedido.

Cálculo Automático: O valor total do pedido é calculado automaticamente com base nos subtotais dos itens.

Seleção de Cliente: Utiliza Combobox para vincular o pedido a um cliente existente.

Filtro por Data (Extensão): Permite filtrar a lista de pedidos por um intervalo de datas (AAAA-MM-DD).

📐 UX e Robustez

Prevenção de Perda de Dados: Alerta o usuário antes de fechar formulários com dados não salvos.

Feedback Visual: Fornece mensagens amigáveis (messagebox) de sucesso e falha.

Tratamento de Erros: Captura erros de banco de dados (try/except) com logs simples e notificação ao usuário.

📤 Extensões de Exportação

Exportação de Pedido: Permite exportar os detalhes de um pedido selecionado para:

CSV: Formato tabular.

PDF Simples: Arquivo de texto (.txt) formatado como relatório.

📁 Estrutura do Projeto

O projeto é modularizado nos seguintes arquivos:

gerenciador_pedidos/
├── db.py                 # Lógica de conexão, inicialização e acesso parametrizado ao SQLite. Inclui funções de Transação.
├── cliente_form.py       # Janela Toplevel para CRUD de Clientes e validações de campos.
├── pedido_form.py        # Janela Toplevel para criação de Pedidos e gerenciamento de Itens (lógica transacional).
├── export_utils.py       # Utilitários para exportação de dados de pedidos (CSV e PDF Simples/TXT).
└── main_app.py           # Ponto de entrada. Aplicação principal com listas, busca, Treeviews e abas.


⚙️ Pré-requisitos

Para executar esta aplicação, você precisa ter o Python instalado. As bibliotecas utilizadas são padrão e geralmente já vêm com a instalação do Python, mas o Tkinter (para a GUI) e o módulo csv são obrigatórios.

# Se o Tkinter não estiver instalado (comum em algumas distribuições Linux)
sudo apt-get install python3-tk 


🚀 Como Executar

Clone o repositório (ou baixe os arquivos db.py, cliente_form.py, pedido_form.py, export_utils.py e main_app.py).

Execute o arquivo principal:

python main_app.py


O banco de dados SQLite (gerenciador_pedidos.db) será criado automaticamente na primeira execução do main_app.py.

🗄️ Estrutura do Banco de Dados

O banco de dados gerenciador_pedidos.db contém as seguintes tabelas e relacionamentos:

Tabela

Colunas (Campos Chave/Relacionamento)

Detalhes

clientes

id (PK), nome, email, telefone

email é UNIQUE.

pedidos

id (PK), cliente_id (FK), data, total

Chave estrangeira para clientes com ON DELETE CASCADE.

itens_pedido

id (PK), pedido_id (FK), produto, quantidade, preco_unit

Chave estrangeira para pedidos com ON DELETE CASCADE.

🖼️ Imagens do Aplicativo
