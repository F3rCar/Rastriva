from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisResponse, AnalysisUpdate
from app.services.analysis_service import AnalysisService

router = APIRouter()
service = AnalysisService()
DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/", response_model=AnalysisResponse, status_code=status.HTTP_200_OK
)
async def create_analysis(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Formato inválido. Envie um arquivo .csv ou .xlsx",
        )

    result = await service.process_analysis(file)
    analysis = Analysis(
        name=Path(file.filename).stem,
        file_name=file.filename,
        status="completed",
        metricas=result["metricas"],
        graficos=result["graficos"],
        diagnostico=result["diagnostico"],
    )

    try:
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Não foi possível salvar a análise.",
        ) from exc

    return analysis


@router.get("/", response_model=list[AnalysisResponse])
def list_analyses(db: DbSession):
    try:
        return db.scalars(
            select(Analysis).order_by(Analysis.created_at.desc())
        ).all()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Não foi possível listar as análises."
        ) from exc


@router.put("/{analysis_id}", response_model=AnalysisResponse)
def update_analysis(
    analysis_id: UUID, changes: AnalysisUpdate, db: DbSession
):
    try:
        analysis = db.get(Analysis, analysis_id)
        if analysis is None:
            raise HTTPException(status_code=404, detail="Análise não encontrada.")

        for field, value in changes.model_dump(exclude_unset=True).items():
            setattr(analysis, field, value)

        db.commit()
        db.refresh(analysis)
        return analysis
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Não foi possível atualizar a análise."
        ) from exc


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(analysis_id: UUID, db: DbSession):
    try:
        analysis = db.get(Analysis, analysis_id)
        if analysis is None:
            raise HTTPException(status_code=404, detail="Análise não encontrada.")

        db.delete(analysis)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Não foi possível excluir a análise."
        ) from exc
