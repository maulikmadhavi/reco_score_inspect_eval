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

// YlGnBu colorscale as explicit RGB stops, so we can compute the actual
// cell color and pick a contrasting text color from its brightness.
const COLORSCALE = [
  [0.000, [255, 255, 217]],
  [0.125, [237, 248, 177]],
  [0.250, [199, 233, 180]],
  [0.375, [127, 205, 187]],
  [0.500, [65, 182, 196]],
  [0.625, [29, 145, 192]],
  [0.750, [34, 94, 168]],
  [0.875, [37, 52, 148]],
  [1.000, [8, 29, 88]],
];

function colorAt(t) {
  // linearly interpolate the RGB color at position t in [0, 1]
  for (let k = 1; k < COLORSCALE.length; k++) {
    const [p0, c0] = COLORSCALE[k - 1];
    const [p1, c1] = COLORSCALE[k];
    if (t <= p1) {
      const f = (t - p0) / (p1 - p0);
      return c0.map((c, idx) => c + f * (c1[idx] - c));
    }
  }
  return COLORSCALE[COLORSCALE.length - 1][1];
}

function textColorFor(t) {
  // perceived brightness (ITU-R BT.601); dark text on light cells, white on dark
  const [r, g, b] = colorAt(t);
  const brightness = 0.299 * r + 0.587 * g + 0.114 * b;
  return brightness > 140 ? "#1e1e2e" : "#ffffff";
}

function drawMatrix(matrix) {
  const { gt_labels, pred_labels, counts } = matrix;
  const maxCount = Math.max(1, ...counts.flat());

  const trace = {
    x: pred_labels,
    y: gt_labels,
    z: counts,
    type: "heatmap",
    colorscale: COLORSCALE.map(([p, rgb]) => [p, `rgb(${rgb.join(",")})`]),
    zmin: 0,
    zmax: maxCount,
    showscale: true,
    hovertemplate: "gt=%{y} &rarr; pred=%{x}<br>count=%{z}<extra></extra>",
  };

  // count label in each cell, colored to contrast its own cell background
  const annotations = [];
  gt_labels.forEach((gt, i) => {
    pred_labels.forEach((pred, j) => {
      const count = counts[i][j];
      annotations.push({
        x: pred,
        y: gt,
        text: String(count),
        showarrow: false,
        font: { color: textColorFor(count / maxCount), size: 14 },
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
