# AdCUE — Explainable, Scene-Aware Ad Overlays (Solo AI PM Case Study)

**Repo:** https://github.com/vbhima09/adcue-starter  
**Live demo:** _add your Hugging Face Space link_  
**Owner:** Viharika Bhimanapati

---

## 1) Executive Summary
AdCUE is a lightweight ad-tech prototype that **places contextually relevant ad overlays** on short videos while **explaining every decision**.  
It uses a **safe‑zone heuristic** to avoid occlusions and a **LinUCB contextual bandit** to pick the best *(ad × placement)* for a given topic and viewer cohort, learning over impressions.

**Why it matters:** creators and small publishers need higher eCPM without hurting UX. AdCUE demonstrates a transparent, measurable path to uplift with clear safety guardrails.

---

## 2) Problem & Goals
- **Problem:** manual, opaque ad placement slows teams and risks covering faces/text.  
- **MVP Goal:** ship a demo that (1) produces **brand‑safe overlays**, (2) **learns** which placements perform, and (3) **explains why** each choice was made.  
- **North‑star:** show the bandit beating a random baseline on simulated clicks while keeping overlays within safe zones.

**Guardrails:** 0 intentional occlusion (heuristic), <3s to first preview, exportable JSON decision log.

---

## 3) What I Built
- **Preview overlay:** first frame extracted with ffmpeg → safe box computed → ad composited.  
- **Learning loop:** actions are *(ad × placement)*; LinUCB explores/exploits using topic + cohort features.  
- **Explainability:** each decision emits a JSON log with topic, cohort, action, safe box, and last reward.

---

## 4) Screenshots (Examples)

### Video 1 — Overlay & Learning
<img src="assets/screenshots/Video_1_Preview_OL.png" width="900"/>
<img src="assets/screenshots/Vide0_1_Graphs.png" width="900"/>

**Decision snapshot (last impression)**  
**Topic** `outdoor`, **Cohort** `travelers` → **ad_id** `1` at **bottom-left`` (placement_id=0) | **safe box** `{'x': 50, 'y': 366, 'w': 254, 'h': 86}` | **last click** `0`  
`artifacts/decisions/video_1_decision_log.json`

---

### Video 2 — Overlay & Learning
<img src="assets/screenshots/Video_2_Preview_OL.png" width="900"/>
<img src="assets/screenshots/Video_2_Graphs.png" width="900"/>

**Decision snapshot (last impression)**  
**Topic** `outdoor`, **Cohort** `travelers` → **ad_id** `1` at **top-left`` (placement_id=2) | **safe box** `{'x': 50, 'y': 28, 'w': 254, 'h': 86}` | **last click** `0`  
`artifacts/decisions/Video_2_decision_log.json`

---

### Video 3 — Overlay & Learning
<img src="assets/screenshots/Video_3_Preview_OL.png" width="900"/>
<img src="assets/screenshots/Video_3_Graph.png" width="900"/>

**Decision snapshot (last impression)**  
**Topic** `outdoor`, **Cohort** `travelers` → **ad_id** `3` at **bottom-right`` (placement_id=1) | **safe box** `{'x': 544, 'y': 366, 'w': 254, 'h': 86}` | **last click** `0`  
`artifacts/decisions/Video_3_decision_log.json`

> Note: the `clicked` field shown is the reward from the **last** simulated impression only. The uplift in the charts is **cumulative** across the run.

---

## 5) Results Snapshot
Across three example runs (300 impressions each), the **bandit finished ahead of the random baseline** on cumulative clicks in every run (see charts above). This demonstrates the core product promise: **learning‑driven placement choices** that improve over time while honoring safety constraints.

**Metrics I track and report**
- **Learning:** bandit cumulative clicks vs random.  
- **Safety:** % previews within the safe zone (no intentional center occlusion).  
- **Latency:** time to first preview.

---

## 6) Safety & Explainability
- **Safe‑zone heuristic:** avoids a protected center region + margins (proxy for faces/text) and chooses one of the four corners with nudging if overlap is detected.  
- **Decision transparency:** every run yields a **JSON decision** with topic, cohort, *(ad × placement)*, safe box geometry, and last reward; these can be audited or replayed later.  
- **Content licensing:** source videos are CC/Pexels; a `sources.csv` log is kept outside Git to respect repo size limits.

---

## 7) Business Impact (illustrative)
If a publisher’s overlay unit has baseline CTR **1.5%**, and the bandit improves relative CTR by **~25–40%** (typical in these simulations), CTR becomes **1.9–2.1%**.  
With CPM $10 and 100k impressions, that improvement yields **$40–$60** incremental value for that unit (higher if conversions are monetized).  
*This demo is designed to be validated quickly with a small live pilot.*

---

## 8) What I’d Ship Next (Production Path)
1) **Real detectors**: YOLO for faces/objects + OCR for text; temporal smoothing to keep overlays stable ≥2s.  
2) **Brand suitability**: allow/block lists by category with “blocked reasons” in the UI.  
3) **Policy objective**: optimize CTR − occlusion_penalty − aesthetic_penalty (CLIP‑based).  
4) **Integrations**: VAST/VPAID export or a small overlay SDK (Video.js/JW Player).  
5) **Consent & labeling**: “Ad” disclosure and preference storage; lightweight attribution for clicks.

---

## 9) How to Reproduce
```bash
# Windows
python -m venv .venv
.\.venv\Scriptsctivate
pip install -r requirements.txt
# (Optional) place ffmpeg.exe next to app.py for video frame extraction
streamlit run app.py
```
Upload a short MP4 or image → choose topic & cohort → preview overlay → run the learning simulation → export the decision log JSON.

---

## 10) Artifacts
- Screenshots & charts:  
  `assets/screenshots/Video_1_Preview_OL.png`, `assets/screenshots/Vide0_1_Graphs.png`  
  `assets/screenshots/Video_2_Preview_OL.png`, `assets/screenshots/Video_2_Graphs.png`  
  `assets/screenshots/Video_3_Preview_OL.png`, `assets/screenshots/Video_3_Graph.png`

- Decision logs (last‑impression snapshots):  
  `artifacts/decisions/video_1_decision_log.json`  
  `artifacts/decisions/Video_2_decision_log.json`  
  `artifacts/decisions/Video_3_decision_log.json`