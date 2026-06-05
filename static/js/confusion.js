const confusionDiv = document.getElementById("confusion");
const imageStrip = document.getElementById("image-strip");
const cellTitle = document.getElementById("cell-title");

// ── Init ──────────────────────────────────────────────────────────────────────

async function init() {
  const res = await fetch("/api/confusion");
  const matrix = await res.json();
  drawMatrix(matrix);
}

// ── Confusion matrix heatmap ──────────────────────────────────────────────────

function drawMatrix(matrix) {
  const { gt_labels, pred_labels, counts } = matrix;

  const trace = {
    x: pred_labels,
    y: gt_labels,
    z: counts,
    type: "heatmap",
    colorscale: "Blues",
    showscale: true,
    hovertemplate: "gt=%{y} &rarr; pred=%{x}<br>count=%{z}<extra></extra>",
  };

  // count label drawn inside each cell
  const annotations = [];
  gt_labels.forEach((gt, i) => {
    pred_labels.forEach((pred, j) => {
      annotations.push({
        x: pred,
        y: gt,
        text: String(counts[i][j]),
        showarrow: false,
        font: { color: "#222", size: 13 },
      });
    });
  });

  const layout = {
    margin: { t: 10, r: 10, b: 50, l: 60 },
    xaxis: { title: "Predicted", side: "bottom" },
    yaxis: { title: "Ground truth", autorange: "reversed" },
    annotations: annotations,
    plot_bgcolor: "#fff",
    paper_bgcolor: "#fff",
    height: 360,
  };

  Plotly.react(confusionDiv, [trace], layout, { responsive: true, displayModeBar: false });

  confusionDiv.on("plotly_click", (data) => {
    const point = data.points[0];
    loadCell(point.y, point.x);  // y = ground truth, x = predicted
  });
}

// ── Cell images ───────────────────────────────────────────────────────────────

async function loadCell(gt, pred) {
  const url = `/api/confusion/cell?gt=${encodeURIComponent(gt)}&pred=${encodeURIComponent(pred)}`;
  const res = await fetch(url);
  const { images } = await res.json();

  const kind = gt === pred ? "correct" : "error";
  cellTitle.textContent = `gt = ${gt} → pred = ${pred}  (${images.length} ${kind}, by confidence)`;

  imageStrip.innerHTML = "";
  if (!images || images.length === 0) {
    imageStrip.innerHTML = `<span id="empty-msg">No images in this cell.</span>`;
    return;
  }

  images.forEach(img => {
    const card = document.createElement("div");
    card.className = "img-card";

    const el = document.createElement("img");
    el.src = `/image?path=${encodeURIComponent(img.path)}`;
    el.alt = img.name;
    el.loading = "lazy";

    const nameEl = document.createElement("div");
    nameEl.className = "img-name";
    nameEl.textContent = img.name;

    const scoreEl = document.createElement("div");
    scoreEl.className = "img-score";
    scoreEl.textContent = img.score.toFixed(4);

    card.appendChild(el);
    card.appendChild(nameEl);
    card.appendChild(scoreEl);
    imageStrip.appendChild(card);
  });
}

// ── Start ─────────────────────────────────────────────────────────────────────

init();
