from fastapi import UploadFile
from app.ai.agent import gerar_diagnostico_ia
from app.analysis.processor import processar_dados_cliente


class AnalysisService:

    async def process_analysis(self, file: UploadFile) -> dict:
        content = await file.read()

        # 1. Processar a planilha
        dados = processar_dados_cliente(content, file.filename)

        # 2. Gerar diagnóstico com IA
        diagnostico = gerar_diagnostico_ia(dados["metricas"])

        # 3. Retornar payload completo
        return {
            "metricas": dados["metricas"],
            "graficos": dados["graficos"],
            "diagnostico": diagnostico,
        }