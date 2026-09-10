# Rastriva

A Rastriva é uma plataforma em desenvolvimento para ajudar pequenas e médias
empresas a identificar sinais de afastamento de clientes e apoiar decisões de
retenção. Este repositório contém apenas a estrutura técnica inicial do projeto.

## Estrutura

- `backend/`: API FastAPI e testes automatizados.
- `frontend/`: página estática provisória para testar a API.
- `data/examples/`: arquivos CSV fictícios para uso futuro.
- `docs/`: documentação inicial do contrato da API, regras e CSVs.

## Requisitos

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- Uma extensão como Live Server para servir o frontend na porta 5500

## Backend

No PowerShell:

```powershell
cd backend
uv sync
uv run fastapi dev app/main.py
```

A API ficará disponível em `http://127.0.0.1:8000`. Para verificar o serviço,
acesse `http://127.0.0.1:8000/api/v1/health`.

## Testes e qualidade

Dentro de `backend/`, execute:

```powershell
uv run pytest
uv run ruff check .
uv run ruff format .
```

## Frontend

Abra `frontend/index.html` com o Live Server na porta 5500. Depois, use o botão
**Testar conexão com a API**. O backend precisa estar em execução na porta 8000.
