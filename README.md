# Rastriva

A Rastriva ajuda pequenas e médias empresas a identificar sinais de perda de clientes e planejar ações de retenção. O backend é uma API FastAPI com PostgreSQL; o frontend é uma página estática que envia uma planilha e apresenta a análise.

## Estrutura

- `backend/`: API, processamento de planilhas, modelo de dados e migrations Alembic.
- `frontend/`: página HTML, CSS e JavaScript com gráficos Chart.js.
- `data/examples/`: arquivos CSV para testes.
- `docs/`: documentação do projeto.

## Pré-requisitos

- Python 3.12 ou superior e [uv](https://docs.astral.sh/uv/).
- PostgreSQL em execução e um banco de dados já criado para a aplicação.
- Para abrir o frontend, a extensão [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) no VS Code ou outro servidor de arquivos estáticos.

## Preparar o backend

No PowerShell, a partir da raiz do repositório:

```powershell
cd backend
uv sync
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Edite `backend/.env` e substitua a URL de exemplo pela conexão do seu PostgreSQL. A variável deve ter este formato:

```text
DATABASE_URL=postgresql+psycopg://USUARIO:SENHA@localhost:5432/NOME_DO_BANCO
```

O arquivo `.env` é ignorado pelo Git. Não coloque credenciais reais em `.env.example`.

Com o banco já criado, aplique a migration existente e inicie a API:

```powershell
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

A API ficará disponível em `http://127.0.0.1:8000` e a documentação interativa em `http://127.0.0.1:8000/docs`. Mantenha esse terminal aberto.

## Testar a API

Abra `http://127.0.0.1:8000/docs`, escolha `POST /api/v1/analyses/`, clique em **Try it out**, selecione `data/examples/vendas.csv` no campo **file** e clique em **Execute**.

A resposta bem-sucedida retorna HTTP 200 com `id`, `name`, `file_name`, `status: "completed"`, `metricas`, `graficos`, `diagnostico`, `created_at` e `updated_at`. O resultado também é salvo na tabela `analyses`; o conteúdo do arquivo não é armazenado. A rota aceita um arquivo `.csv`, `.xlsx` ou `.xls` por requisição.

Para conferir a gravação no PostgreSQL, execute no banco configurado:

```sql
SELECT id, name, file_name, status, created_at FROM analyses ORDER BY created_at DESC LIMIT 5;
```

Os testes automatizados usam uma sessão de banco simulada e não precisam de PostgreSQL. Em outro terminal, dentro de `backend`:

```powershell
uv run pytest -q
```

Execute os comandos de `uv` a partir de `backend`; a configuração dos imports e testes está no `backend/pyproject.toml`.

## Testar pelo frontend

1. Deixe a API rodando em `http://127.0.0.1:8000`.
2. No VS Code, abra `frontend/index.html` com **Open with Live Server**. Se usar outro servidor estático, abra a página pelo endereço fornecido por ele.
3. Na página, clique em **Upload do arquivo** e escolha `data/examples/vendas.csv`.
4. Aguarde a mensagem de conclusão. Os cartões, gráficos e textos de diagnóstico serão atualizados com a resposta da API. Confira também o novo registro em `analyses` usando a consulta SQL acima.

O frontend envia o arquivo no campo `file` para `http://127.0.0.1:8000/api/v1/analyses/`. Ele aceita uma planilha por vez; os arquivos `clientes.csv` e `feedbacks.csv` não são campos separados da rota atual.

O diagnóstico exibido será o texto de exemplo definido no backend quando a variável de ambiente `GEMINI_API_KEY` não estiver disponível para o processo da API. Os percentuais de feedback e parte das séries dos gráficos também contêm valores fixos no processamento atual.
