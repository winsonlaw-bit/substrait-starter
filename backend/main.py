"""
Volumetric weight calculator — a single backend that serves both its web page
and its API.

Substrait requires three things of this file:
  1. the server listens on port 8000          (set in cicd/Dockerfile.backend)
  2. GET /health returns 200                  (Substrait's readiness check)
  3. the JSON API lives under /api            (Substrait routes /api here)

Because this project has no frontend/ folder, Substrait sends ALL traffic to this
backend — including "/" — so this file also serves the page you see in the browser.
"""

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

APP_NAME = "体积重量计算器"

app = FastAPI(title=APP_NAME, docs_url="/api/docs")


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}


@app.get("/api/volumetric-weight", tags=["calculator"])
def volumetric_weight(
    length: float = Query(ge=0, description="Package length in centimeters"),
    width: float = Query(ge=0, description="Package width in centimeters"),
    height: float = Query(ge=0, description="Package height in centimeters"),
):
    """Calculate volumetric (billable) weight from package dimensions."""
    divisor = 5000
    weight = (length * width * height) / divisor
    return {
        "length_cm": length,
        "width_cm": width,
        "height_cm": height,
        "divisor": divisor,
        "volumetric_weight_kg": round(weight, 4),
    }


PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>体积重量计算器</title>
<style>
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    min-height: 100vh;
    display: grid;
    place-items: center;
    font: 16px/1.6 ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    background: linear-gradient(180deg, #f4f7fb 0%, #eef2f7 100%);
    color: #172033;
    padding: 32px 24px;
  }
  .layout {
    width: 100%;
    max-width: 460px;
  }
  .hero {
    margin-bottom: 18px;
    text-align: left;
  }
  .hero h1 {
    margin: 0;
    font-size: clamp(1.8rem, 4vw, 2.4rem);
    line-height: 1.1;
    letter-spacing: -0.03em;
    color: #0f172a;
  }
  .hero p {
    margin: 10px 0 0;
    color: #526076;
    font-size: 15px;
  }
  .card {
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 22px;
    padding: 32px;
    width: 100%;
    box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
    backdrop-filter: blur(14px);
  }
  .field {
    margin-bottom: 18px;
  }
  .field label {
    display: block;
    margin-bottom: 6px;
    font-size: 14px;
    font-weight: 600;
    color: #41506a;
  }
  .input-wrap {
    display: flex;
    align-items: center;
    border: 1px solid rgba(148, 163, 184, 0.4);
    border-radius: 12px;
    overflow: hidden;
    transition: border-color 0.15s;
  }
  .input-wrap:focus-within {
    border-color: #3b82f6;
  }
  .input-wrap input {
    flex: 1;
    border: none;
    outline: none;
    padding: 12px 16px;
    font: 16px ui-sans-serif, system-ui, sans-serif;
    color: #0f172a;
    background: transparent;
    -moz-appearance: textfield;
  }
  .input-wrap input::-webkit-outer-spin-button,
  .input-wrap input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  .input-wrap .unit {
    padding-right: 16px;
    color: #94a3b8;
    font-size: 14px;
  }
  .result {
    margin-top: 24px;
    padding: 24px;
    border-radius: 16px;
    background: #f0f7ff;
    border: 1px solid rgba(59, 130, 246, 0.15);
    text-align: center;
  }
  .result .label {
    font-size: 14px;
    color: #526076;
    margin-bottom: 4px;
  }
  .result .value {
    font-size: 2.4rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.03em;
  }
  .result .value .unit {
    font-size: 1.2rem;
    color: #526076;
    font-weight: 500;
  }
  .result .formula {
    margin-top: 12px;
    font-size: 13px;
    color: #94a3b8;
  }
  .result .formula code {
    background: rgba(59, 130, 246, 0.08);
    padding: 2px 6px;
    border-radius: 5px;
    font-size: 12px;
    color: #41506a;
  }
</style>
</head>
<body>
  <div class="layout">
    <section class="hero">
      <h1>体积重量计算器</h1>
      <p>输入包裹尺寸，计算计费重量。</p>
    </section>

    <main class="card">
      <div class="field">
        <label for="len">长度</label>
        <div class="input-wrap">
          <input id="len" type="number" min="0" step="0.1" placeholder="0" autocomplete="off">
          <span class="unit">cm</span>
        </div>
      </div>
      <div class="field">
        <label for="wid">宽度</label>
        <div class="input-wrap">
          <input id="wid" type="number" min="0" step="0.1" placeholder="0" autocomplete="off">
          <span class="unit">cm</span>
        </div>
      </div>
      <div class="field">
        <label for="hgt">高度</label>
        <div class="input-wrap">
          <input id="hgt" type="number" min="0" step="0.1" placeholder="0" autocomplete="off">
          <span class="unit">cm</span>
        </div>
      </div>

      <div class="result" id="result">
        <div class="label">计费重量</div>
        <div class="value" id="result-value">0.00 <span class="unit">kg</span></div>
        <div class="formula"><code>(长 × 宽 × 高) ÷ 5000</code></div>
      </div>
    </main>
  </div>

<script>
  const inputs = ['len', 'wid', 'hgt'].map(id => document.getElementById(id));
  const resultValue = document.getElementById('result-value');

  function calc() {
    const [l, w, h] = inputs.map(i => parseFloat(i.value) || 0);
    const weight = (l * w * h) / 5000;
    resultValue.innerHTML = weight.toFixed(2) + ' <span class="unit">kg</span>';
  }

  inputs.forEach(i => i.addEventListener('input', calc));
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def homepage():
    return PAGE
