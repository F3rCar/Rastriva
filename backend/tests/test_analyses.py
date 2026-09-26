from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.routes.analyses import service
from app.db.session import get_db
from app.main import app

client = TestClient(app)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SALES_FILE = PROJECT_ROOT / "data" / "examples" / "vendas.csv"


class FakeSession:
    def __init__(self, *, fail_on_commit: bool = False) -> None:
        self.added = []
        self.committed = False
        self.rolled_back = False
        self.fail_on_commit = fail_on_commit

    def add(self, instance) -> None:
        self.added.append(instance)

    def commit(self) -> None:
        if self.fail_on_commit:
            from sqlalchemy.exc import SQLAlchemyError

            raise SQLAlchemyError("database unavailable")
        self.committed = True

    def refresh(self, instance) -> None:
        instance.id = uuid4()
        instance.created_at = datetime.now()
        instance.updated_at = instance.created_at

    def rollback(self) -> None:
        self.rolled_back = True


@pytest.fixture
def fake_db():
    session = FakeSession()
    app.dependency_overrides[get_db] = lambda: session
    yield session
    app.dependency_overrides.clear()


@pytest.fixture
def processed_result(monkeypatch):
    async def process_analysis(_file):
        return {
            "metricas": {
                "clientes_analisados": 10,
                "clientes_risco": 2,
                "receita_risco": 100.0,
            },
            "graficos": {
                "consumidores": [5, 2, 1, 2],
                "feedbacks_pct": {"preco": 50.0},
                "padroes_labels": [],
                "disponibilidade": [],
                "quantidade_compras": [],
                "receita": [],
            },
            "diagnostico": {
                "problema_identificado": "risco",
                "causas_provaveis": "causa",
                "clientes_impactados": "clientes",
                "resposta_agente": "resposta",
                "plano_alta": "alta",
                "plano_media": "media",
                "plano_baixa": "baixa",
            },
        }

    monkeypatch.setattr(service, "process_analysis", process_analysis)


def test_processed_analysis_is_saved(fake_db, processed_result) -> None:
    response = client.post(
        "/api/v1/analyses/",
        files={"file": ("vendas.csv", SALES_FILE.read_bytes(), "text/csv")},
    )

    assert response.status_code == 200
    assert fake_db.committed is True
    saved = fake_db.added[0]
    assert saved.name == "vendas"
    assert saved.file_name == "vendas.csv"
    assert saved.status == "completed"
    assert response.json()["file_name"] == "vendas.csv"
    assert response.json()["metricas"] == saved.metricas


def test_database_error_rolls_back(processed_result) -> None:
    session = FakeSession(fail_on_commit=True)
    app.dependency_overrides[get_db] = lambda: session
    try:
        response = client.post(
            "/api/v1/analyses/",
            files={"file": ("vendas.csv", b"conteudo", "text/csv")},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500
    assert session.rolled_back is True


def test_invalid_extension_is_rejected(fake_db) -> None:
    response = client.post(
        "/api/v1/analyses/",
        files={"file": ("vendas.txt", b"conteudo", "text/plain")},
    )

    assert response.status_code == 400
    assert fake_db.added == []


def test_file_is_required(fake_db) -> None:
    response = client.post("/api/v1/analyses/")

    assert response.status_code == 422
    assert fake_db.added == []
