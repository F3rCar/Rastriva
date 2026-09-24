# Rastriva

A Rastriva é uma plataforma desenvolvida para ajudar pequenas e médias empresas a identificar sinais de desinteresse ou abandono (churn) de clientes e a tomar ações de retenção preventivas através de inteligência artificial.

## Estrutura do Projeto

- `backend/`: API FastAPI (Python) com processamento de dados (Pandas) e integração com IA.
- `frontend/`: Interface web estática (HTML, CSS, JavaScript) com gráficos interativos em Chart.js.
- `data/examples/`: Ficheiros CSV/Excel de exemplo para testes.
- `docs/`: Documentação e especificações de dados.

## Requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Gestor de dependências Python)
- Extensão [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) no VS Code (para o frontend)

## Configuração do Backend

1. Entra na pasta do backend e instala as dependências:
   ```powershell
   cd backend
   uv sync
   uv add pandas openpyxl google-genai
