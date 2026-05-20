const palette = ["#1f7a6d", "#c2533f", "#315f9d", "#bd8b22", "#6d5a9c", "#44724b", "#8b4d6b"];

function moneylessFormat(value) {
  return Number(value).toLocaleString("es-CO", { maximumFractionDigits: 1 });
}

async function getDashboardData() {
  const sources = ["/api/status", "../data/mart/dashboard_data.json"];
  for (const source of sources) {
    try {
      const response = await fetch(source, { cache: "no-store" });
      if (response.ok) return response.json();
    } catch (error) {
      // GitHub Pages does not have the local Python API, so try the static JSON.
    }
  }
  throw new Error("No fue posible cargar los datos del dashboard.");
}

function drawBarChart(canvasId, rows, options = {}) {
  const canvas = document.getElementById(canvasId);
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  const padding = { top: 20, right: 24, bottom: 80, left: 56 };
  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;
  const maxValue = Math.max(...rows.map((row) => Number(row.value)), 1);

  ctx.clearRect(0, 0, width, height);
  ctx.strokeStyle = "#d7e1de";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding.left, padding.top);
  ctx.lineTo(padding.left, padding.top + chartH);
  ctx.lineTo(padding.left + chartW, padding.top + chartH);
  ctx.stroke();

  rows.forEach((row, index) => {
    const barGap = 12;
    const slot = chartW / rows.length;
    const barW = Math.max(22, slot - barGap);
    const value = Number(row.value);
    const barH = (value / maxValue) * (chartH - 8);
    const x = padding.left + index * slot + barGap / 2;
    const y = padding.top + chartH - barH;

    ctx.fillStyle = palette[index % palette.length];
    ctx.fillRect(x, y, barW, barH);
    ctx.fillStyle = "#16201f";
    ctx.font = "16px Arial";
    ctx.textAlign = "center";
    ctx.fillText(options.percent ? `${moneylessFormat(value)}%` : moneylessFormat(value), x + barW / 2, y - 8);

    ctx.save();
    ctx.translate(x + barW / 2, padding.top + chartH + 14);
    ctx.rotate(-Math.PI / 5);
    ctx.font = "13px Arial";
    ctx.textAlign = "right";
    ctx.fillStyle = "#5f6f6d";
    ctx.fillText(String(row.label).replaceAll("_", " "), 0, 0);
    ctx.restore();
  });
}

function renderTable(rows) {
  const table = document.getElementById("sampleTable");
  table.innerHTML = "";
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    [
      row.person_id,
      row.age,
      row.gender,
      row.bmi,
      row.bmi_category,
      row.physical_activity_score,
      row.habit_risk_score,
      row.obesity_level,
    ].forEach((value) => {
      const td = document.createElement("td");
      td.textContent = value;
      tr.appendChild(td);
    });
    table.appendChild(tr);
  });
}

function renderDashboard(data) {
  document.getElementById("kpiRecords").textContent = moneylessFormat(data.kpis.records);
  document.getElementById("kpiBmi").textContent = moneylessFormat(data.kpis.avg_bmi);
  document.getElementById("kpiOverweight").textContent = `${moneylessFormat(data.kpis.obesity_or_overweight_pct)}%`;
  document.getElementById("kpiRisk").textContent = moneylessFormat(data.kpis.avg_habit_risk_score);

  const status = document.getElementById("statusBox");
  const generated = new Date(data.metadata.generated_at).toLocaleString("es-CO");
  status.textContent = `${data.metadata.message} Registros: ${data.metadata.records}. Generado: ${generated}. Fuente: ${data.metadata.source_page}`;

  drawBarChart("obesityChart", data.charts.obesity_level);
  drawBarChart("bmiChart", data.charts.bmi_category);
  drawBarChart("ageRiskChart", data.charts.risk_by_age_group);
  drawBarChart("transportChart", data.charts.transportation);
  renderTable(data.sample);
}

async function load() {
  const data = await getDashboardData();
  renderDashboard(data);
}

document.getElementById("refreshBtn").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  button.disabled = true;
  button.textContent = "Actualizando...";
  try {
    const response = await fetch("/api/refresh", { cache: "no-store" });
    if (!response.ok) throw new Error("Modo estatico");
    await load();
  } catch (error) {
    await load();
    document.getElementById("statusBox").textContent +=
      " En GitHub Pages se muestran los datos publicados; para refrescar desde UCI ejecuta el pipeline localmente y sube los cambios.";
  } finally {
    button.disabled = false;
    button.textContent = "Actualizar datos";
  }
});

load().catch((error) => {
  document.getElementById("statusBox").textContent = error.message;
});
