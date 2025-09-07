# AdCUE — Explainable, Scene-Aware Ad Overlay (Starter)

This is a **portfolio-ready starter** for a tiny AI ad-tech demo you can deploy publicly.
It focuses on **explainable safe zones**, a **lightweight contextual bandit** (LinUCB) to choose (ad, placement),
and a simple **Streamlit** app to preview overlays and simulate learning (CTR uplift).

## What works in this starter
- Upload a **video (MP4)** *or* a **single image**.
- Extract a preview frame (first frame) if `ffmpeg` is available; otherwise upload an image.
- Choose a viewer cohort and topics (manual for now) to simulate context.
- Place a sample ad in a computed **safe zone** (simple heuristic that avoids margins).
- Run a **Bandit vs Random** simulation and see CTR curves.
- Export the decision log (JSON).

> This starter intentionally avoids heavy ML deps so you can deploy fast (Hugging Face Spaces / Vercel + Streamlit).
> You can later swap the heuristics with Whisper/YOLO/real taggers.

## Quickstart (local)
```bash
# 1) clone or unzip this repo
cd adcue-starter

# 2) (optional) create venv
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3) install deps
pip install -r requirements.txt

# 4) run the app
streamlit run app.py
```

Visit: http://localhost:8501

## Deploy to Hugging Face Spaces
1. Create a **new Space** → SDK: **Streamlit**.
2. Push this repository to the Space (connect from GitHub or upload).
3. That’s it — the Space will build and serve `app.py` automatically.

## Project structure
```
adcue-starter/
├── app.py                 # Streamlit UI
├── requirements.txt
├── LICENSE
├── .gitignore
├── README.md
├── src/
│   ├── linucb.py          # LinUCB contextual bandit
│   └── utils/
│       ├── decisions.py   # decision logs & schemas
│       └── simulate.py    # simple CTR simulator
├── assets/
│   ├── ads/               # sample ad images (PNG)
│   └── sample_frames/     # optional sample images
├── data/
│   ├── raw_videos/        # put your MP4 here (gitignored)
│   ├── audio/             # (future) extracted WAVs (gitignored)
│   └── frames/            # extracted frames (gitignored)
└── scripts/
    └── extract_frames.sh  # optional ffmpeg helper
```

## Roadmap (how to extend)
- Replace safe-zone heuristic with actual detections (faces/text/objects) and temporal smoothing.
- Add topic/tag extraction via Whisper (transcript) + a keyword/topic lexicon.
- Store runs & events to a DB (e.g., Supabase) and plot historical metrics.
- Add VAST/VPAID-compatible export.

## Ethics & Safety
- Use Creative Commons or your own content only.
- The app watermarks "Demo Overlay" on exports.
- Avoid sensitive categories by default.