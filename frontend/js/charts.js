(() => {
  const consumersCanvas = document.getElementById("chartConsumidores");
  const patternsCanvas = document.getElementById("chartPadroes");

  if (!consumersCanvas || !patternsCanvas || typeof Chart === "undefined") return;

  const palette = {
    text: "#555555",
    grid: "#cccccc",
    consumers: ["#a020f0", "#3b9fe0", "#e0d63b", "#3b4fe0"],
    availability: "red",
    purchases: "blue",
    revenue: "green",
  };
  const currency = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    maximumFractionDigits: 0,
  });
  const compactCurrency = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    notation: "compact",
    maximumFractionDigits: 1,
  });

  Chart.defaults.color = palette.text;
  Chart.defaults.font.family = "Arial, Helvetica, sans-serif";
  Chart.defaults.font.size = 11;

  const consumers = new Chart(consumersCanvas, {
    type: "bar",
    data: {
      labels: [
        "Clientes ativos",
        "Clientes em queda",
        "Clientes com possível risco",
        "Histórico insuficiente",
      ],
      datasets: [
        {
          label: "Clientes",
          data: [0, 0, 0, 0],
          backgroundColor: palette.consumers,
          borderRadius: 4,
          borderSkipped: false,
          maxBarThickness: 56,
        },
      ],
    },
    options: {
      indexAxis: "x",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (context) => ` ${context.parsed.y.toLocaleString("pt-BR")} clientes`,
          },
        },
      },
      scales: {
        x: {
          grid: { display: false },
          border: { display: false },
        },
        y: {
          beginAtZero: true,
          ticks: { precision: 0 },
          grid: { color: palette.grid },
          border: { display: false },
        },
      },
    },
  });

  const patterns = new Chart(patternsCanvas, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Disponibilidade",
          data: [],
          yAxisID: "y",
          borderColor: palette.availability,
          backgroundColor: palette.availability,
          borderWidth: 2.5,
          pointRadius: 3,
          pointHoverRadius: 5,
          tension: 0.28,
        },
        {
          label: "Quantidade de compras",
          data: [],
          yAxisID: "y",
          borderColor: palette.purchases,
          backgroundColor: palette.purchases,
          borderWidth: 2.5,
          pointRadius: 3,
          pointHoverRadius: 5,
          tension: 0.28,
        },
        {
          label: "Receita",
          data: [],
          yAxisID: "yRevenue",
          borderColor: palette.revenue,
          backgroundColor: palette.revenue,
          borderWidth: 2.5,
          pointRadius: 3,
          pointHoverRadius: 5,
          tension: 0.28,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (context) => {
              const value = context.parsed.y;
              if (context.dataset.yAxisID === "yRevenue") {
                return ` ${context.dataset.label}: ${currency.format(value)}`;
              }
              if (context.dataset.label === "Disponibilidade") {
                return ` ${context.dataset.label}: ${value}%`;
              }
              return ` ${context.dataset.label}: ${value.toLocaleString("pt-BR")}`;
            },
          },
        },
      },
      scales: {
        x: {
          grid: { color: palette.grid },
          border: { display: false },
        },
        y: {
          beginAtZero: true,
          grid: { color: palette.grid },
          border: { display: false },
        },
        yRevenue: {
          beginAtZero: true,
          position: "right",
          grid: { drawOnChartArea: false },
          border: { display: false },
          ticks: { callback: (value) => compactCurrency.format(value) },
        },
      },
    },
  });

  window.rastrivaCharts = { consumers, patterns };
})();