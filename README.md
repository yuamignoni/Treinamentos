# Sistema de Treinamentos

## Descrição

Este projeto é um sistema de gerenciamento de treinamentos de funcionários, permitindo a criação de usuários com diferentes níveis de acesso, gerenciamento de funcionários e seus treinamentos, e funcionalidades de busca avançada.

## Funcionalidades

- **Criação de Usuários**: Permite a criação de usuários com três níveis de acesso:
  - **Admin**: Acesso a todas as funcionalidades.
  - **Gerente**: Acesso a todas as funcionalidades, exceto criação de usuários.
  - **Funcionário**: Apenas visualização dos treinamentos.
- **Gerenciamento de Funcionários**: Adição e visualização de funcionários.
- **Gerenciamento de Treinamentos**: Adição, atualização e exclusão de treinamentos para funcionários.
- **Busca Avançada**: Possibilidade de busca na tela de treinamentos por usuário ou por tipo de treinamento.

## Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: Tkinter (Python)
- **Banco de Dados**: SQLite e Postgres

## Instruções para Iniciar a Aplicação

### Requisitos

- **Python**: Certifique-se de ter o Python instalado.
- **Bibliotecas Python**: Requests, sqlite3, tkinter.

### Passos para Iniciar

## Configuração do Ambiente

### Passo 1: Clonar o Repositório

Clone o repositório para sua máquina local:

```bash
git clone https://github.com/yuamignoni/Treinamentos.git
cd Treinamentos
```

### Passo 2: Inicializar o Banco de Dados e o Servidor Flask

Utilize Docker Compose para configurar o banco de dados e o servidor Flask:

```bash
docker-compose up -d
```

Este comando irá criar e iniciar os containers necessários para o banco de dados e o servidor Flask.

### Passo 3: Instalar Dependências

Certifique-se de que você tenha o Python 3.x instalado. Instale as dependências do projeto:

```bash
pip install -r requirements.txt
```

## Executar a Aplicação

Para iniciar a aplicação, execute o seguinte comando:

```bash
py main.py
```

## Notas

- **Sincronização:** A aplicação sincroniza automaticamente a base de dados local com o servidor Flask.
- **Interface:** A interface gráfica foi desenvolvida com Tkinter e inclui funcionalidades de busca e gerenciamento de dados.
