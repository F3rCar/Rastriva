from app.schemas.analysis import AnalysisResponse
from app.services.analysis_service import AnalysisService
from fastapi import APIRouter, File, HTTPException, UploadFile, status

router = APIRouter()
service = AnalysisService()


@router.post(
    "/", response_model=AnalysisResponse, status_code=status.HTTP_200_OK
)
async def create_analysis(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Formato inválido. Envie um arquivo .csv ou .xlsx",
        )

    return await service.process_analysis(file)