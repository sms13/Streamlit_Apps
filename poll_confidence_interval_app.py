"""Run with: streamlit run poll_confidence_interval_app.py"""

from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


def normal_interval(proportion: float, sample_size: int) -> tuple[float, float]:
    """Return the approximate 95% normal interval, bounded to [0, 1]."""
    z = 1.96
    half_width = z * sqrt(proportion * (1 - proportion) / sample_size)
    return max(0.0, proportion - half_width), min(1.0, proportion + half_width)


st.set_page_config(page_title="Candidate Poll Confidence Interval", layout="wide")
st.title("How precise is a candidate poll?")
st.markdown(
    """<style>
    [data-testid="stSliderTickBar"] { display: none; }
    </style>""",
    unsafe_allow_html=True,
)


st.subheader("Number of people polled (n)")
sample_size = st.slider(
    "Number of people polled (n)", 30, 1_000, 30, step=10,
    label_visibility="collapsed",
)
st.markdown(
    '<div style="display: flex; justify-content: space-between; font-size: 1rem; opacity: 1;">'
    '<span>30</span><span>1,000</span></div>',
    unsafe_allow_html=True,
)
st.subheader("Sample proportion in favor of Candidate A")
input_proportion = st.number_input(
    "Sample proportion in favor of Candidate A",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.01,
    format="%.2f",
    width=140,
    label_visibility="collapsed",
)
settings = (sample_size, input_proportion)
if st.session_state.get("poll_settings") != settings:
    st.session_state.poll_settings = settings
    st.session_state.poll_votes_a = None

if st.button("Run new sample", type="primary"):
    st.session_state.poll_votes_a = int(
        np.random.default_rng().binomial(sample_size, input_proportion)
    )

votes_a = st.session_state.poll_votes_a
proportion = input_proportion if votes_a is None else votes_a / sample_size
if votes_a is not None:
    st.caption(f"Latest poll: {votes_a:,} prefer A; {sample_size - votes_a:,} prefer B.")

lower, upper = normal_interval(proportion, sample_size)

half_width = (upper - lower) / 2

fig, ax = plt.subplots(figsize=(11, 3.4))
ax.plot([0, 1], [0, 0], color="#CBD5E1", linewidth=5, solid_capstyle="round")
ax.plot(
    [lower, upper], [0, 0], color="#2F6F73", linewidth=9,
    solid_capstyle="butt", label="95% confidence interval",
)
ax.scatter([lower, upper], [0, 0], marker="|", s=220, color="#2F6F73", zorder=3)
ax.scatter([proportion], [0], s=100, color="#B23A48", zorder=4, label="Observed proportion")
ax.annotate(f"{lower:.3f}", (lower, 0), xytext=(0, -25), textcoords="offset points", ha="center")
ax.annotate(f"{upper:.3f}", (upper, 0), xytext=(0, -25), textcoords="offset points", ha="center")
ax.annotate(
    f"{proportion:.3f}", (proportion, 0), xytext=(0, -42),
    textcoords="offset points", ha="center", color="#B23A48",
)
interval_midpoint = (lower + upper) / 2
ax.vlines([interval_midpoint, upper], 0.08, 0.25, color="#64748B", linewidth=1)
ax.annotate(
    "", xy=(upper, 0.22), xytext=(interval_midpoint, 0.22),
    arrowprops={"arrowstyle": "<->", "color": "#2F6F73", "shrinkA": 0, "shrinkB": 0},
)
ax.text(
    (interval_midpoint + upper) / 2, 0.30,
    f"Half-width = {half_width:.3f}",
    ha="center" if 0.15 <= interval_midpoint <= 0.85 else ("left" if interval_midpoint < 0.15 else "right"),
    va="bottom", color="#2F6F73", fontsize=11,
)
ax.set_xlim(0, 1)
ax.set_ylim(-0.5, 0.5)
ax.set_xticks([])
ax.annotate("0", (0, 0), xytext=(-10, 0), textcoords="offset points", ha="right", va="center")
ax.annotate("1", (1, 0), xytext=(10, 0), textcoords="offset points", ha="left", va="center")
ax.set_yticks([])
ax.set_xlabel("Proportion of people who prefer candidate A")
for spine in ax.spines.values():
    spine.set_visible(False)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.25), ncol=2, frameon=False)
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)
