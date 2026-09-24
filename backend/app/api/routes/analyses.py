from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.schemas.analysis import AnalysisResponse
from app.services.analysis_service import AnalysisService

router = APIRouter()
service = AnalysisService()

@router.post("/", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def create_analysis(file: UploadFile = File(...)):
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(
            status_code=400, 
            detail="Formato de arquivo inválido. Envie um arquivo CSV ou Excel."
        )
    return await service.process_analysis(file)