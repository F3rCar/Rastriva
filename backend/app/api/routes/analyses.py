from pathlib import Path

from app.db.session import get_db
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisResponse
from app.services.analysis_service import AnalysisService
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

router = APIRouter()
service = AnalysisService()


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
