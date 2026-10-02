from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes.analyses import service
from app.db.session import get_db
from app.main import app
from app.models.analysis import Analysis

client = TestClient(app)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SALES_FILE = PROJECT_ROOT / "data" / "examples" / "vendas.csv"


class FakeSession:
    def __init__(
        self, *, records: list[Analysis] | None = None,
        fail_on_commit: bool = False, fail_on_read: bool = False
    ) -> None:
        self.added = []
        self.deleted = []
        self.records = records if records is not None else []
        self.committed = False
        self.rolled_back = False
        self.fail_on_commit = fail_on_commit
        self.fail_on_read = fail_on_read
        self.query = None

    def add(self, instance) -> None:
        self.added.append(instance)

    def commit(self) -> None:
        if self.fail_on_commit:
            raise SQLAlchemyError("database unavailable")
        self.committed = True

    def refresh(self, instance) -> None:
        if instance.id is None:
            instance.id = uuid4()
        if instance.created_at is None:
            instance.created_at = datetime.now(UTC)
        if instance.updated_at is None:
            instance.updated_at = instance.created_at

    def scalars(self, query):
        if self.fail_on_read:
            raise SQLAlchemyError("database unavailable")
        self.query = query
        return self

    def all(self) -> list[Analysis]:
        return sorted(self.records, key=lambda item: item.created_at, reverse=True)

    def get(self, _model, analysis_id: UUID) -> Analysis | None:
        if self.fail_on_read:
            raise SQLAlchemyError("database unavailable")
        return next(
            (item for item in self.records if item.id == analysis_id), None
        )

    def delete(self, instance: Analysis) -> None:
        self.deleted.append(instance)
        self.records.remove(instance)

    def rollback(self) -> None:
        self.rolled_back = True


@pytest.fixture
def fake_db():
    session = FakeSession()
    app.dependency_overrides[get_db] = lambda: session
    yield session
    app.dependency_overrides.clear()


@pytest.fixture
def saved_analysis() -> Analysis:
    return Analysis(
        id=uuid4(),
        name="vendas",
        file_name="vendas.csv",
        status="completed",
        metricas={
            "clientes_analisados": 10,
            "clientes_risco": 2,
            "receita_risco": 100.0,
        },
        graficos={
            "consumidores": [5, 2, 1, 2],
            "feedbacks_pct": {"preco": 50.0},
            "padroes_labels": [],
            "disponibilidade": [],
            "quantidade_compras": [],
            "receita": [],
        },
        diagnostico={
            "problema_identificado": "risco",
            "causas_provaveis": "causa",
            "clientes_impactados": "clientes",
            "resposta_agente": "resposta",
            "plano_alta": "alta",
            "plano_media": "media",
            "plano_baixa": "baixa",
        },
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


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


def test_list_analyses_newest_first(fake_db, saved_analysis) -> None:
    saved_analysis.created_at -= timedelta(days=1)
    newer = Analysis(
        id=uuid4(),
        name="novas vendas",
        file_name="novas.csv",
        status="completed",
        metricas=saved_analysis.metricas,
        graficos=saved_analysis.graficos,
        diagnostico=saved_analysis.diagnostico,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    fake_db.records.extend([saved_analysis, newer])

    response = client.get("/api/v1/analyses/")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [
        str(newer.id), str(saved_analysis.id)
    ]
    assert "ORDER BY analyses.created_at DESC" in str(fake_db.query)


def test_list_analyses_empty(fake_db) -> None:
    response = client.get("/api/v1/analyses/")

    assert response.status_code == 200
    assert response.json() == []


def test_list_database_error_rolls_back(fake_db) -> None:
    fake_db.fail_on_read = True

    response = client.get("/api/v1/analyses/")

    assert response.status_code == 500
    assert fake_db.rolled_back is True


def test_update_existing_analysis(fake_db, saved_analysis) -> None:
    fake_db.records.append(saved_analysis)
    response = client.put(
        f"/api/v1/analyses/{saved_analysis.id}",
        json={"name": "Vendas atualizadas", "status": "completed"},
    )

    assert response.status_code == 200
    assert fake_db.committed is True
    assert response.json()["name"] == "Vendas atualizadas"
    assert saved_analysis.name == "Vendas atualizadas"
    assert saved_analysis.file_name == "vendas.csv"
    assert response.json()["metricas"] == saved_analysis.metricas


def test_update_missing_analysis(fake_db) -> None:
    response = client.put(
        f"/api/v1/analyses/{uuid4()}", json={"name": "Não existe"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Análise não encontrada."
    assert fake_db.committed is False


def test_update_rejects_other_fields(fake_db, saved_analysis) -> None:
    fake_db.records.append(saved_analysis)
    response = client.put(
        f"/api/v1/analyses/{saved_analysis.id}",
        json={"name": "Alterada", "metricas": {}},
    )

    assert response.status_code == 422
    assert saved_analysis.name == "vendas"
    assert fake_db.committed is False


def test_delete_existing_analysis(fake_db, saved_analysis) -> None:
    fake_db.records.append(saved_analysis)
    response = client.delete(f"/api/v1/analyses/{saved_analysis.id}")

    assert response.status_code == 204
    assert response.content == b""
    assert fake_db.deleted == [saved_analysis]
    assert fake_db.committed is True


def test_delete_missing_analysis(fake_db) -> None:
    response = client.delete(f"/api/v1/analyses/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Análise não encontrada."
    assert fake_db.committed is False


@pytest.mark.parametrize("method", ["put", "delete"])
def test_invalid_uuid_returns_422(fake_db, method: str) -> None:
    if method == "put":
        response = client.put(
            "/api/v1/analyses/not-a-uuid", json={"name": "Teste"}
        )
    else:
        response = client.delete("/api/v1/analyses/not-a-uuid")

    assert response.status_code == 422


def test_update_database_error_rolls_back(fake_db, saved_analysis) -> None:
    fake_db.records.append(saved_analysis)
    fake_db.fail_on_commit = True

    response = client.put(
        f"/api/v1/analyses/{saved_analysis.id}", json={"status": "pending"}
    )

    assert response.status_code == 500
    assert fake_db.rolled_back is True


def test_delete_database_error_rolls_back(fake_db, saved_analysis) -> None:
    fake_db.records.append(saved_analysis)
    fake_db.fail_on_commit = True

    response = client.delete(f"/api/v1/analyses/{saved_analysis.id}")

    assert response.status_code == 500
    assert fake_db.rolled_back is True
