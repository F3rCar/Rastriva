const testButton = document.querySelector("#test-api");
const apiStatus = document.querySelector("#api-status");

testButton.addEventListener("click", async () => {
  apiStatus.textContent = "Verificando conexão...";

  try {
    const response = await fetch("http://127.0.0.1:8000/api/v1/health");

    if (!response.ok) {
      throw new Error(`A API respondeu com o status ${response.status}.`);
    }

    const data = await response.json();
    apiStatus.textContent = `${data.service} está online.`;
  } catch (error) {
    apiStatus.textContent = `Não foi possível conectar à API: ${error.message}`;
  }
});
