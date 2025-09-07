import os
import io
import json
import subprocess
from datetime import datetime

import numpy as np
from PIL import Image, ImageOps
# --- bootstrap for Hugging Face Spaces ---
import os, pathlib
# Give Streamlit a writable HOME (Spaces allows /home/user and /tmp)
os.environ.setdefault("HOME", "/home/user")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp")
# Point Streamlit to the repo config file (so it doesn’t look in ~/.streamlit at /)
os.environ.setdefault("STREAMLIT_CONFIG_FILE", str(pathlib.Path(__file__).parent / ".streamlit" / "config.toml"))
# Turn off usage stats programmatically (belt & suspenders)
os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
# -----------------------------------------

import streamlit as st

import streamlit as st
import plotly.graph_objects as go

from src.linucb import LinUCB
from src.utils.simulate import TOPICS, COHORTS, simulate_click, topic_to_vec, cohort_to_vec
from src.utils.decisions import DecisionLog

st.set_page_config(page_title="AdCUE Starter", page_icon="🧩", layout="wide")

st.title("AdCUE — Explainable, Scene-Aware Ad Overlay (Starter)")
st.write("""
Upload a short **video** (MP4) or a **single image**. We'll compute a safe placement box (simple heuristic),
overlay a sample ad, and simulate a **bandit vs random** learning loop for CTR uplift.
""")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("Inputs")
    media_type = st.radio("Media type", ["Video", "Image"], index=0)
    uploaded_video = None
    uploaded_image = None
    if media_type == "Video":
        uploaded_video = st.file_uploader("Upload MP4", type=["mp4"])
    else:
        uploaded_image = st.file_uploader("Upload image", type=["jpg","jpeg","png"])

    topic = st.selectbox("Detected topic (demo)", TOPICS, index=0)
    cohort = st.selectbox("Viewer cohort (demo)", COHORTS, index=0)

    st.header("Placement")
    placement_opts = ["bottom-left", "bottom-right", "top-left", "top-right"]
    # We'll let bandit choose among these actions, but also allow a fixed pick for preview
    fixed_placement = st.selectbox("Preview placement", placement_opts, index=0)

    st.header("Simulation")
    n_impressions = st.slider("Impressions to simulate", 50, 1000, 300, 50)
    alpha = st.slider("LinUCB exploration (alpha)", 0.05, 1.0, 0.25, 0.05)

    st.header("Ad Creative")
    ad_files = sorted([f for f in os.listdir("assets/ads") if f.endswith(".png")])
    ad_index = st.selectbox("Choose ad", list(range(len(ad_files))), format_func=lambda i: ad_files[i])

# --- Helper functions ---
def extract_first_frame(video_bytes) -> Image.Image:
    """Extract the first frame via ffmpeg (if available). Fallback: return None."""
    tmp_in = "tmp_input.mp4"
    tmp_out = "tmp_frame.jpg"
    with open(tmp_in, "wb") as f:
        f.write(video_bytes)
    try:
        cmd = ["ffmpeg", "-y", "-i", tmp_in, "-vf", "select=eq(n\,0)", "-q:v", "3", tmp_out]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        img = Image.open(tmp_out).convert("RGB")
        return img
    except Exception as e:
        return None
    finally:
        for p in [tmp_in, tmp_out]:
            if os.path.exists(p):
                os.remove(p)

def compute_safe_zone(img: Image.Image, placement: str, margin_ratio: float = 0.06):
    """Very simple 'safe zone': place ad within margins; avoid covering the center region."""
    W, H = img.size
    margin_w, margin_h = int(W * margin_ratio), int(H * margin_ratio)
    # Avoid center 40% x 30% as a proxy for faces/text
    center_box = (int(W*0.3), int(H*0.35), int(W*0.7), int(H*0.65))

    # Default ad box size is 30% width, 18% height
    w, h = int(W * 0.3), int(H * 0.18)
    if placement == "bottom-left":
        x = margin_w
        y = H - h - margin_h
    elif placement == "bottom-right":
        x = W - w - margin_w
        y = H - h - margin_h
    elif placement == "top-left":
        x = margin_w
        y = margin_h
    else:  # top-right
        x = W - w - margin_w
        y = margin_h

    # If overlaps the center_box, nudge upward or downward
    def overlaps(a, b):
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)

    box = (x, y, x + w, y + h)
    if overlaps(box, center_box):
        # Nudge by margin
        y = margin_h if y > H//2 else H - h - margin_h
        box = (x, y, x + w, y + h)

    return dict(x=int(x), y=int(y), w=int(w), h=int(h))

def overlay_ad(img: Image.Image, ad_path: str, box: dict) -> Image.Image:
    ad = Image.open(ad_path).convert("RGB")
    ad = ad.resize((box["w"], box["h"]))
    out = img.copy()
    out.paste(ad, (box["x"], box["y"]))
    # Watermark
    wm = ImageOps.expand(Image.new("RGBA", (200, 40), (0,0,0,0)), border=0)
    out_draw = out.copy()
    return out

# --- Load a frame ---
frame = None
content_name = "sample_001.jpg"

if uploaded_image is not None:
    frame = Image.open(uploaded_image).convert("RGB")
    content_name = uploaded_image.name
elif uploaded_video is not None:
    data = uploaded_video.read()
    frame = extract_first_frame(data)
    content_name = uploaded_video.name
    if frame is None:
        st.warning("ffmpeg not available. Please install ffmpeg or upload a still image instead.")
else:
    frame = Image.open("assets/sample_frames/sample_001.jpg").convert("RGB")

# --- Preview with chosen placement ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("Original Frame")
    st.image(frame, use_container_width=True)
with col2:
    st.subheader("Preview with Overlay")
    safe_box = compute_safe_zone(frame, fixed_placement)
    preview = overlay_ad(frame, os.path.join("assets/ads", ad_files[ad_index]), safe_box)
    st.image(preview, use_container_width=True)
    st.caption(f"Placement: {fixed_placement} | Safe box: {safe_box}")

st.markdown("---")

# --- Simulation: Bandit vs Random ---
st.header("Learning Simulation: Bandit vs Random")
st.write("""
We simulate **clicks** for (ad, placement) choices under the selected topic & cohort.
The **bandit** (LinUCB) learns which combos perform better and should beat a **random** policy.
""")

# Define discrete actions = all combinations of (ad, placement)
placements = ["bottom-left", "bottom-right", "top-left", "top-right"]
actions = [(ai, pi) for ai in range(len(ad_files)) for pi in range(len(placements))]
n_actions = len(actions)

# Context vector = one-hot(topic) + one-hot(cohort)
x_topic = topic_to_vec(topic)
x_cohort = cohort_to_vec(cohort)
context = np.concatenate([x_topic, x_cohort], axis=0)
dim = context.shape[0]

# Bandit learner
bandit = LinUCB(n_actions=n_actions, dim=dim, alpha=alpha)

# Run simulation
bandit_clicks = 0
random_clicks = 0
xs, by, ry = [], [], []
logs = []

for t in range(n_impressions):
    # Bandit chooses action
    a_idx = bandit.select(context)
    ad_id, placement_id = actions[a_idx]
    clicked = simulate_click(topic, cohort, ad_id, placement_id)
    bandit.update(context, a_idx, clicked)
    bandit_clicks += clicked
    xs.append(t+1); by.append(bandit_clicks)

    # Random baseline
    ra_idx = np.random.randint(0, n_actions)
    rad_id, rplacement_id = actions[ra_idx]
    r_clicked = simulate_click(topic, cohort, rad_id, rplacement_id)
    random_clicks += r_clicked
    ry.append(random_clicks)

    if t == n_impressions - 1:
        # Log final decision preview
        chosen_place = placements[placement_id]
        safe_box = compute_safe_zone(frame, chosen_place)
        reason = f"Topic={topic}, Cohort={cohort}, prior bandit reward~{bandit_clicks/max(1,t):.3f}"
        logs.append(DecisionLog(
            content_name=content_name,
            topic=topic,
            cohort=cohort,
            ad_id=int(ad_id),
            placement_id=int(placement_id),
            reason=reason,
            safe_zone=safe_box,
            clicked=int(clicked),
        ).to_json())

# Plot cumulative clicks
fig = go.Figure()
fig.add_trace(go.Scatter(x=xs, y=by, mode='lines', name='Bandit cumulative clicks'))
fig.add_trace(go.Scatter(x=xs, y=ry, mode='lines', name='Random cumulative clicks'))
fig.update_layout(xaxis_title="Impressions", yaxis_title="Cumulative clicks")
st.plotly_chart(fig, use_container_width=True)

uplift = (bandit_clicks - random_clicks) / max(1, random_clicks) * 100.0
st.success(f"Bandit clicks: {bandit_clicks} | Random clicks: {random_clicks} | Estimated uplift: {uplift:.1f}%")

# Decision log download
st.download_button("Download last decision log (JSON)", data="\n".join(logs), file_name="decision_log.json")

st.markdown("""
#### Why chosen?
- The bandit explores/exploits combinations of **ad** × **placement** using the provided topic & cohort.
- The preview shows a simple **safe zone** (margin + center avoidance). Replace with detectors when you extend it.
- All choices are explainable and exportable as JSON.
""")