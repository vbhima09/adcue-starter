import numpy as np
from typing import Dict, List

# Simple topic & cohort universe
TOPICS = ["kitchen", "outdoor", "gaming", "fitness", "city"]
COHORTS = ["foodies", "travelers", "gamers", "athletes", "commuters"]

# Map (topic, cohort, ad_id, placement_id) -> base CTR
# Keep it small and hand-crafted for a demo.
def base_ctr(topic: str, cohort: str, ad_id: int, placement_id: int) -> float:
    # Start with a neutral base
    ctr = 0.02
    # Positive affinities
    if topic == "kitchen" and cohort == "foodies" and ad_id == 0:
        ctr += 0.06
    if topic == "gaming" and cohort == "gamers" and ad_id == 1:
        ctr += 0.05
    if topic == "fitness" and cohort == "athletes" and ad_id == 2:
        ctr += 0.05
    if topic == "outdoor" and cohort == "travelers" and ad_id == 3:
        ctr += 0.04

    # Placement tweaks (e.g., bottom-left works best)
    if placement_id == 0:  # bottom-left
        ctr += 0.01
    elif placement_id == 1:  # bottom-right
        ctr += 0.005

    # Clamp to [0.001, 0.5]
    return float(max(0.001, min(ctr, 0.5)))

def simulate_click(topic: str, cohort: str, ad_id: int, placement_id: int, noise: float = 0.01) -> int:
    p = base_ctr(topic, cohort, ad_id, placement_id)
    # Add small Gaussian noise to be less deterministic
    p = float(max(0.0001, min(0.9, np.random.normal(p, noise))))
    return int(np.random.rand() < p)

def topic_to_vec(topic: str) -> np.ndarray:
    vec = np.zeros(len(TOPICS))
    if topic in TOPICS:
        vec[TOPICS.index(topic)] = 1.0
    return vec

def cohort_to_vec(cohort: str) -> np.ndarray:
    vec = np.zeros(len(COHORTS))
    if cohort in COHORTS:
        vec[COHORTS.index(cohort)] = 1.0
    return vec