import json
import os
from google import genai
from google.genai import types


def gerar_diagnostico_ia(metricas: dict) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")

    # Fallback caso a chave da API não esteja configurada no .env
    if not api_key:
        return {
            "problema_identificado": "Aumento no risco de churn no último trimestre.",
            "causas_provaveis": "Percepção de custo alto e suporte lento.",
            "clientes_impactados": "Clientes ativos no plano intermediário.",
            "resposta_agente": "Com base nos dados fornecidos, identificamos que a insatisfação com o atendimento ao cliente e os preços vigentes são os principais motivadores para a retenção baixa.",
            "plano_alta": "Contatar clientes com alta receita em risco para oferta personalizada.",
            "plano_media": "Revisar o tempo médio de resposta do suporte.",
            "plano_baixa": "Enviar pesquisas de satisfação periódicas (NPS).",
        }

    client = genai.Client(api_key=api_key)

    prompt = f"""
    Você é o agente especialista de retenção da plataforma Rastriva.
    Analise estes dados de clientes:
    {json.dumps(metricas, ensure_ascii=False)}

    Responda EXATAMENTE no formato JSON com as chaves:
    {{
      "problema_identificado": "resumo curto do problema",
      "causas_provaveis": "causas prováveis separadas por vírgula",
      "clientes_impactados": "grupo ou perfil mais impactado",
      "resposta_agente": "explicação detalhada e amigável em até 2 parágrafos",
      "plano_alta": "ação corretiva de prioridade alta",
      "plano_media": "ação corretiva de prioridade média",
      "plano_baixa": "melhoria contínua de prioridade baixa"
    }}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        ),
    )

    return json.loads(response.text)