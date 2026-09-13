from typing import Any


# exemplo de função service para chamar a análise dos dados
def run_analysis(
    vendas: bytes,
    clientes: bytes | None = None,
    feedbacks: bytes | None = None,
) -> dict[str, Any]:
    return {
        "data_quality": {
            "status": "pending",
            "warnings": [],
        },
        "summary": {
            "message": "Motor de análise ainda não conectado.",
        },
        "at_risk_customers": [],
        "customer_metrics": [],
        "feedback_patterns": [],
        "recommendations": [],
    }

