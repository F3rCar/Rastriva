from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.analysis import AnalysisResponse
from app.services.analysis_service import run_analysis

router = APIRouter()

MAX_UPLOAD_SIZE = 10 * 1024 * 1024


async def read_csv_file(file: UploadFile | None) -> bytes | None:
    if file is None:
        return None

    filename = (file.filename or "").lower()

    if not filename.endswith(".csv"):
        raise HTTPException(
            status_code=415,
            detail={
                "code": "INVALID_FILE_TYPE",
                "message": "O arquivo deve estar no formato CSV.",
                "field": file.filename,
            },
        )

    content = await file.read(MAX_UPLOAD_SIZE + 1)

    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail={
                "code": "FILE_TOO_LARGE",
                "message": "O arquivo excede o tamanho máximo permitido.",
                "field": file.filename,
            },
        )

    return content


@router.post("/analyses", response_model=AnalysisResponse)
async def create_analysis(
    vendas: Annotated[UploadFile, File()],
    clientes: Annotated[UploadFile | None, File()] = None,
    feedbacks: Annotated[UploadFile | None, File()] = None,
) -> AnalysisResponse:
    vendas_content = await read_csv_file(vendas)
    clientes_content = await read_csv_file(clientes)
    feedbacks_content = await read_csv_file(feedbacks)

    result = run_analysis(
        vendas=vendas_content,
        clientes=clientes_content,
        feedbacks=feedbacks_content,
    )

    return AnalysisResponse.model_validate(result)
