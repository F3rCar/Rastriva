from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SALES_FILE = PROJECT_ROOT / "data" / "examples" / "vendas.csv"
CUSTOMERS_FILE = PROJECT_ROOT / "data" / "examples" / "clientes.csv"
FEEDBACKS_FILE = PROJECT_ROOT / "data" / "examples" / "feedbacks.csv"


def test_create_analysis_with_sales_file() -> None:
    files = {
        "vendas": (
            "vendas.csv",
            SALES_FILE.read_bytes(),
            "text/csv",
        )
    }

    response = client.post("/api/v1/analyses", files=files)

    assert response.status_code == 200

    body = response.json()

    assert "data_quality" in body
    assert "summary" in body
    assert "at_risk_customers" in body
    assert "customer_metrics" in body
    assert "feedback_patterns" in body
    assert "recommendations" in body


def test_create_analysis_with_all_files() -> None:
    files = {
        "vendas": ("vendas.csv", SALES_FILE.read_bytes(), "text/csv"),
        "clientes": ("clientes.csv", CUSTOMERS_FILE.read_bytes(), "text/csv"),
        "feedbacks": (
            "feedbacks.csv",
            FEEDBACKS_FILE.read_bytes(),
            "text/csv",
        ),
    }

    response = client.post("/api/v1/analyses", files=files)

    assert response.status_code == 200
    assert response.json()["summary"] == {
        "message": "Motor de análise ainda não conectado."
    }


def test_rejects_file_with_invalid_extension() -> None:
    files = {"vendas": ("vendas.txt", b"conteudo", "text/plain")}

    response = client.post("/api/v1/analyses", files=files)

    assert response.status_code == 415
    assert response.json()["detail"]["code"] == "INVALID_FILE_TYPE"


def test_rejects_file_larger_than_limit() -> None:
    files = {
        "vendas": (
            "vendas.csv",
            b"x" * (10 * 1024 * 1024 + 1),
            "text/csv",
        )
    }

    response = client.post("/api/v1/analyses", files=files)

    assert response.status_code == 413
    assert response.json()["detail"]["code"] == "FILE_TOO_LARGE"


def test_requires_sales_file() -> None:
    response = client.post("/api/v1/analyses")

    assert response.status_code == 422
