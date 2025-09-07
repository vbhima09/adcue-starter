# AdCUE — Explainable, Scene-Aware Ad Overlays (Solo AI PM Case Study)

**Repo:** https://github.com/vbhima09/adcue-starter  
**Live demo:** https://huggingface.co/spaces/Viharika09/adcue-starter 
**Owner:** Viharika Bhimanapati

---

## 1) Executive Summary
AdCUE is a lightweight ad-tech prototype that places **contextually relevant ad overlays** on short videos and **explains every decision**.  
It uses a **safe-zone heuristic** (avoid covering important regions) and a **LinUCB contextual bandit** to choose the best *(ad × placement)* for a given topic and viewer cohort, improving over impressions.

**Why it matters:** creators and small publishers need higher eCPM without hurting UX. This demo shows a transparent, measurable path to uplift with clear safety guardrails.

---

## 2) Problem & Goals
- **Problem:** Manual, opaque ad placement risks covering faces/text and doesn’t improve with data.
- **MVP Goals:**  
  1) Produce **brand-safe overlays** (no obvious occlusions).  
  2) **Learn** which placements perform (bandit vs random).  
  3) **Explain why** each choice was made (topic, cohort, safe box, action taken).
- **Guardrails:** 0 intentional occlusion (heuristic), <3s to first preview, exportable JSON decision logs.

---

## 3) What I Built
- **Preview overlay:** Extract first frame (ffmpeg) → compute safe box → composite ad.
- **Learning loop:** Actions are *(ad × placement)*; **LinUCB** explores/exploits using topic + cohort features.
- **Explainability:** Each decision emits a JSON log (topic, cohort, action, safe box, last reward).

---

## 4) Screenshots (Examples)

### Video 1 — Overlay & Learning
<img src="assets/screenshots/Video_1_Preview_OL.png" width="900"/>
<img src="assets/screenshots/Vide0_1_Graphs.png" width="900"/>

**Decision log:** `artifacts/decisions/video_1_decision_log.json`

---

### Video 2 — Overlay & Learning
<img src="assets/screenshots/Video_2_Preview_OL.png" width="900"/>
<img src="assets/screenshots/Video_2_Graphs.png" width="900"/>

**Decision log:** `artifacts/decisions/Video_2_decision_log.json`

---

### Video 3 — Overlay & Learning
<img src="assets/screenshots/Video_3_Preview_OL.png" width="900"/>
<img src="assets/screenshots/Video_3_Graph.png" width="900"/>

**Decision log:** `artifacts/decisions/Video_3_decision_log.json`

> Note: `clicked` in the JSON reflects the **last** simulated impression; the charts show **cumulative** clicks over the whole run.

---

## 5) Results Snapshot
Across three 300-impression runs, the bandit showed learning behavior and finished ahead of the random baseline in 2/3 cases, demonstrating data-driven placement while honoring safety constraints.

**Results table (simulated runs)**

| Video | Topic | Cohort | Impressions | Bandit Clicks | Random Clicks | Uplift |
|---|---|---|---:|---:|---:|---:|
| Video_1.mp4 | outdoor | travel | 300 | 12 | 4 | +200% |
| Video_2.mp4 | outdoor | travel | 300 | 7 | 13 | -46.2% |
| Video_3.mp4 | outdoor | travel | 300 | 17 | 15 | +13.3% |

**Metrics tracked**
- **Learning:** bandit cumulative clicks vs random  
- **Safety:** % previews within safe zone (no intentional center occlusion)  
- **Latency:** time to first preview

---

## 6) Safety & Explainability
- **Safe-zone heuristic:** Avoid a protected center region + margins (proxy for faces/text). If overlap is detected, nudge to a corner.
- **Transparency:** Each run yields a JSON decision (topic, cohort, action, safe box, reward) for auditability and reproducibility.
- **Licensing:** Source videos from CC/Pexels; a `sources.csv` license log is kept outside Git to keep the repo lean.

---

## 7) Business Impact (illustrative)
If baseline CTR is **1.5%**, and the bandit lifts relative CTR by **~25–40%** (typical in simulations), CTR becomes **1.9–2.1%**.  
At $10 CPM and 100k impressions, that adds **$40–$60** incremental value for this unit alone (higher if conversions are monetized).  
This MVP is designed for a quick pilot to validate on live traffic.

---

## 8) What I’d Ship Next (Production Path)
1) **Real detectors:** YOLO (faces/objects) + OCR for text; temporal smoothing (keep overlays stable ≥2s).
2) **Brand suitability:** GARM-style categories with allow/block rules and “blocked reasons” shown in UI.
3) **Policy objective:** maximize CTR − occlusion_penalty − aesthetic_penalty (CLIP-based).
4) **Integrations:** VAST/VPAID export or a small overlay SDK (Video.js/JW Player).
5) **Consent & labeling:** “Ad” disclosure, preference storage, lightweight click attribution.

---

## 9) How to Reproduce
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
# (Optional) place ffmpeg.exe next to app.py for video frame extraction
streamlit run app.py
