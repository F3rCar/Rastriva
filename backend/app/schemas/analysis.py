from datetime import datetime
from typing import Dict, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MetricasSchema(BaseModel):
    clientes_analisados: int
    clientes_risco: int
    receita_risco: float


class GraficosSchema(BaseModel):
    consumidores: List[
        int
    ]  # [ativos, em_queda, possivel_risco, historico_insuficiente]
    feedbacks_pct: Dict[
        str, float
    ]  # {"preco": 75.0, "atendimento": 40.0, "geral": 60.0}
    padroes_labels: List[str]
    disponibilidade: List[float]
    quantidade_compras: List[float]
    receita: List[float]


class DiagnosticoIASchema(BaseModel):
    problema_identificado: str
    causas_provaveis: str
    clientes_impactados: str
    resposta_agente: str
    plano_alta: str
    plano_media: str
    plano_baixa: str


class AnalysisResponse(BaseModel):
    id: UUID
    name: str
    file_name: str
    status: str
    metricas: MetricasSchema
    graficos: GraficosSchema
    diagnostico: DiagnosticoIASchema
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AnalysisUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    status: str | None = Field(default=None, min_length=1)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def require_valid_changes(self) -> "AnalysisUpdate":
        if not self.model_fields_set or any(
            getattr(self, field) is None for field in self.model_fields_set
        ):
            raise ValueError("Informe name ou status com um valor não vazio.")
        return self
