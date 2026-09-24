document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.querySelector(".input_arquivo");

  if (!fileInput) return;

  fileInput.addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      //1. Enviar ficheiro para a API FastAPI
      const response = await fetch("http://127.0.0.1:8000/api/v1/analyses/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Erro na API: status ${response.status}`);
      }

      const data = await response.json();

      //2. Atualizar Métrica
      const metricCards = document.querySelectorAll(".metric-card");
      if (metricCards.length >= 3) {
        metricCards[0].textContent = `Clientes analisados: ${data.metricas.clientes_analisados}`;
        metricCards[1].textContent = `Clientes em risco: ${data.metricas.clientes_risco}`;
        metricCards[2].textContent = `Receita em risco: R$ ${data.metricas.receita_risco.toLocaleString("pt-BR")}`;
      }

      //3. Atualizar Gráfico de Consumidores (Barras)
      const chartConsumidores = Chart.getChart("chartConsumidores");
      if (chartConsumidores) {
        chartConsumidores.data.datasets[0].data = data.graficos.consumidores;
        chartConsumidores.update();
      }

      //4. Atualizar Barras de Feedback
      document.getElementById("feedback-preco-fill").style.width = `${data.graficos.feedbacks_pct.preco}%`;
      document.getElementById("feedback-atendimento-fill").style.width = `${data.graficos.feedbacks_pct.atendimento}%`;
      document.getElementById("feedback-feedbacks-fill").style.width = `${data.graficos.feedbacks_pct.geral}%`;

      //5. Atualizar Gráfico de Padrões (Linhas)
      const chartPadroes = Chart.getChart("chartPadroes");
      if (chartPadroes) {
        chartPadroes.data.labels = data.graficos.padroes_labels;
        chartPadroes.data.datasets[0].data = data.graficos.disponibilidade;
        chartPadroes.data.datasets[1].data = data.graficos.quantidade_compras;
        chartPadroes.data.datasets[2].data = data.graficos.receita;
        chartPadroes.update();
      }

      //6. Atualizar Seção de Diagnóstico da IA
      const resumos = document.querySelectorAll(".resumo-card p");
      if (resumos.length >= 3) {
        resumos[0].textContent = data.diagnostico.problema_identificado;
        resumos[1].textContent = data.diagnostico.causas_provaveis;
        resumos[2].textContent = data.diagnostico.clientes_impactados;
      }

      document.querySelector(".ai-response-body").textContent = data.diagnostico.resposta_agente;

      const planos = document.querySelectorAll(".plano-item p");
      if (planos.length >= 3) {
        planos[0].textContent = data.diagnostico.plano_alta;
        planos[1].textContent = data.diagnostico.plano_media;
        planos[2].textContent = data.diagnostico.plano_baixa;
      }

      alert("Análise concluída com sucesso!");

    } catch (error) {
      console.error("Erro ao processar ficheiro:", error);
      alert(`Falha no envio: ${error.message}`);
    }
  });
});