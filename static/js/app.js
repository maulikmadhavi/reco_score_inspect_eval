let currentCategory = null;
let debounceTimer = null;

const categorySelect = document.getElementById("category-select");
const scoreSlider = document.getElementById("score-slider");
const sliderLabel = document.getElementById("slider-label");
const imageStrip = document.getElementById("image-strip");

// ── Init ──────────────────────────────────────────────────────────────────────

async function init() {
  const res = await fetch("/api/categories");
  const { categories } = await res.json();
  categories.forEach(cat => {
    const opt = document.createElement("option");
    opt.value = cat;
    opt.textContent = cat;
    categorySelect.appendChild(opt);
  });
  if (categories.length > 0) {
    currentCategory = categories[0];
    categorySelect.value = currentCategory;
    await loadDistribution(currentCategory);
  }
}

// ── Category change ───────────────────────────────────────────────────────────

categorySelect.addEventListener("change", async () => {
  currentCategory = categorySelect.value;
  await loadDistribution(currentCategory);
});

// ── Distribution + histogram ──────────────────────────────────────────────────

async function loadDistribution(category) {
  const res = await fetch(`/api/distribution?category=${encodeURIComponent(category)}`);
  const data = await res.json();

  const { scores, min, max } = data;

  // update slider bounds
  const step = parseFloat(((max - min) / 200).toFixed(4)) || 0.005;
  scoreSlider.min = min;
  scoreSlider.max = max;
  scoreSlider.step = step;
  const midScore = parseFloat(((min + max) / 2).toFixed(4));
  scoreSlider.value = midScore;
  sliderLabel.textContent = midScore.toFixed(3);

  drawHistogram(scores, midScore);
  await loadImages(category, midScore);
}

function drawHistogram(scores, selectedScore) {
  const trace = {
    x: scores,
    type: "histogram",
    xbins: { start: 0, end: 1, size: 0.01 },
    marker: { color: "#89b4fa", opacity: 0.8 },
    name: "images",
  };

  const layout = {
    margin: { t: 10, r: 10, b: 40, l: 50 },
    xaxis: { title: "Score", range: [0, 1] },
    yaxis: { title: "Count" },
    shapes: [{
      type: "line",
      x0: selectedScore, x1: selectedScore,
      y0: 0, y1: 1,
      yref: "paper",
      line: { color: "#f38ba8", width: 2, dash: "dot" },
    }],
    plot_bgcolor: "#fff",
    paper_bgcolor: "#fff",
  };

  Plotly.react("histogram", [trace], layout, { responsive: true, displayModeBar: false });
}

function updateHistogramLine(score) {
  Plotly.relayout("histogram", {
    "shapes[0].x0": score,
    "shapes[0].x1": score,
  });
}

// ── Slider ────────────────────────────────────────────────────────────────────

scoreSlider.addEventListener("input", () => {
  const score = parseFloat(scoreSlider.value);
  sliderLabel.textContent = score.toFixed(3);
  updateHistogramLine(score);

  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    loadImages(currentCategory, score);
  }, 150);
});

// ── Image gallery ─────────────────────────────────────────────────────────────

async function loadImages(category, score) {
  const url = `/api/images?category=${encodeURIComponent(category)}&score=${score}&window=10`;
  const res = await fetch(url);
  const { images } = await res.json();

  imageStrip.innerHTML = "";

  if (!images || images.length === 0) {
    imageStrip.innerHTML = `<span id="empty-msg">No images found near this score.</span>`;
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
