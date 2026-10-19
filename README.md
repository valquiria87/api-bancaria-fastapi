# API Bancária Assíncrona

API REST para gerenciamento de contas bancárias e transações, desenvolvida com Python, FastAPI e SQLAlchemy assíncrono.

## Funcionalidades

- Criação de contas bancárias.
- Listagem de contas e histórico de transações.
- Depósitos e saques.
- Validação de saldo suficiente para saques.
- Consulta de extrato bancário.
- Autenticação JWT para transações e consulta de extratos.
- Persistência de dados em SQLite.
- Documentação interativa com Swagger UI.

## Tecnologias

- Python
- FastAPI
- SQLAlchemy assíncrono
- SQLite e aiosqlite
- Pydantic
- JWT com PyJWT
- Uvicorn

## Pré-requisitos

- Python instalado.
- Git instalado.
- Terminal PowerShell ou equivalente.

## Instalação

Clone o repositório:

```bash
git clone https://github.com/valquiria87/api-bancaria-fastapi.git
cd api-bancaria-fastapi
```

Crie e ative um ambiente virtual no Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências necessárias:

```powershell
python -m pip install fastapi uvicorn sqlalchemy aiosqlite PyJWT python-multipart
```

## Configuração das variáveis de ambiente

Configure as credenciais no PowerShell antes de iniciar a API:

```powershell
$env:JWT_SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
$env:API_USERNAME = "admin"
$env:API_PASSWORD = "defina-uma-senha-forte"
```

Use uma senha própria e forte. Não publique senhas, tokens JWT ou a chave secreta no repositório.

Essas variáveis precisam estar configuradas no mesmo terminal em que a API será iniciada.

## Executar a API

```powershell
python -m uvicorn main:app
```

Acesse:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

O banco SQLite é criado localmente quando a aplicação inicia. O arquivo do banco não deve ser publicado no GitHub.

## Autenticação

No Swagger, use a opção **Authorize** para autenticar com as credenciais configuradas. O endpoint `/token` fornece um token JWT.

As rotas de transações e consulta de extrato exigem autenticação.

## Endpoints principais

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/` | Verifica se a API está funcionando |
| POST | `/token` | Autenticação e geração de token |
| POST | `/accounts` | Cria uma conta |
| GET | `/accounts` | Lista contas |
| POST | `/accounts/{account_id}/transactions` | Realiza depósito ou saque |
| GET | `/accounts/{account_id}/statement` | Consulta extrato |

## Validações testadas

- Autenticação obrigatória nas rotas protegidas.
- Rejeição de valores de transação iguais a zero.
- Bloqueio de saques com saldo insuficiente.
- Respostas de erro para conta inexistente.
- Atualização do saldo e registro das transações.

## Objetivo do projeto

Projeto de portfólio para demonstrar conhecimentos em desenvolvimento de APIs REST, Python, FastAPI, programação assíncrona, persistência de dados, validação e autenticação JWT.

## Autora

Valquiria Coelho — GitHub: [@valquiria87](https://github.com/valquiria87)
