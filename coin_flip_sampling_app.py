import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Coin Flip Sampling Distribution", layout="wide")


def init_state() -> None:
    if "sample_heads" not in st.session_state:
        st.session_state.sample_heads = []
    if "last_sample" not in st.session_state:
        st.session_state.last_sample = None
    if "settings" not in st.session_state:
        st.session_state.settings = None


def reset_simulation() -> None:
    st.session_state.sample_heads = []
    st.session_state.last_sample = None


def simulate_samples(num_samples: int, flips_per_sample: int, p_heads: float) -> None:
    heads = np.random.binomial(flips_per_sample, p_heads, size=num_samples)
    st.session_state.sample_heads.extend(heads.tolist())
    st.session_state.last_sample = int(heads[-1])


def make_sampling_distribution_plot(
    sample_proportions: np.ndarray,
    flips_per_sample: int,
    p_heads: float,
):
    possible_props = np.arange(flips_per_sample + 1) / flips_per_sample
    bin_width = 1 / flips_per_sample
    bins = np.append(possible_props - bin_width / 2, possible_props[-1] + bin_width / 2)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.hist(
        sample_proportions,
        bins=bins,
        color="#2F6F73",
        edgecolor="white",
        linewidth=1,
    )
    ax.axvline(
        p_heads,
        color="#B23A48",
        linestyle="--",
        linewidth=2,
        label=f"True p = {p_heads:.2f}",
    )
    ax.set_xlim(-0.02, 1.02)
    ax.set_xlabel("Sample proportion of heads")
    ax.set_ylabel("Number of simulated samples")
    ax.set_title("Sampling Distribution Built From Simulated Coin-Flip Samples")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    return fig


init_state()

st.title("Coin Flip Sampling Distribution")
st.caption(
    "Simulate repeated samples of coin flips and watch the sampling distribution "
    "of the sample proportion of heads take shape."
)

with st.sidebar:
    st.header("Simulation Settings")
    flips_per_sample = st.number_input(
        "Flips per sample",
        min_value=1,
        max_value=1_000,
        value=100,
        step=1,
        help="Each simulation records the proportion of heads in this many flips.",
    )
    p_heads = st.slider(
        "True probability of heads",
        min_value=0.0,
        max_value=1.0,
        value=0.50,
        step=0.01,
    )
    st.button("Reset simulation", on_click=reset_simulation, use_container_width=True)

current_settings = (int(flips_per_sample), float(p_heads))
if st.session_state.settings is None:
    st.session_state.settings = current_settings
elif st.session_state.settings != current_settings:
    reset_simulation()
    st.session_state.settings = current_settings
    st.toast("Settings changed, so the sampling distribution was reset.")

col_one, col_hundred, col_thousand = st.columns([1, 1, 1])
with col_one:
    if st.button("Simulate 1 sample", use_container_width=True):
        simulate_samples(1, int(flips_per_sample), float(p_heads))
with col_hundred:
    if st.button("Simulate 100 more samples", use_container_width=True):
        simulate_samples(100, int(flips_per_sample), float(p_heads))
with col_thousand:
    if st.button("Simulate 1,000 more samples", use_container_width=True):
        simulate_samples(1_000, int(flips_per_sample), float(p_heads))

sample_heads = np.array(st.session_state.sample_heads, dtype=float)
sample_count = len(sample_heads)

metric_cols = st.columns(5)
metric_cols[0].metric("Simulated samples", f"{sample_count:,}")
metric_cols[1].metric("Flips per sample", f"{int(flips_per_sample):,}")
metric_cols[2].metric("True p(heads)", f"{p_heads:.2f}")

if sample_count:
    sample_proportions = sample_heads / flips_per_sample
    mean_prop = sample_proportions.mean()
    metric_cols[3].metric("Mean sample proportion", f"{mean_prop:.3f}")
else:
    sample_proportions = np.array([])
    metric_cols[3].metric("Mean sample proportion", "–")

std_prop = sample_proportions.std(ddof=1) if sample_count > 1 else None
metric_cols[4].metric(
    "Std dev of sample proportions",
    f"{std_prop:.3f}" if std_prop is not None else "–",
    help="Sample standard deviation across simulated proportions (requires at least two samples).",
)

left, right = st.columns([2, 1])

with left:
    if sample_count:
        st.pyplot(
            make_sampling_distribution_plot(
                sample_proportions,
                int(flips_per_sample),
                float(p_heads),
            )
        )
    else:
        st.info("Run a simulation to start building the sampling distribution.")

with right:
    st.subheader("Latest Sample")
    if st.session_state.last_sample is None:
        st.write("No samples simulated yet.")
    else:
        last_heads = st.session_state.last_sample
        last_tails = int(flips_per_sample) - last_heads
        last_prop = last_heads / flips_per_sample
        st.metric("Heads", f"{last_heads:,}")
        st.metric("Tails", f"{last_tails:,}")
        st.metric("Sample proportion", f"{last_prop:.3f}")

if sample_count:
    st.subheader("Simulated Samples")
    display_count = min(sample_count, 100)
    results = pd.DataFrame(
        {
            "Sample #": np.arange(1, sample_count + 1),
            "Proportion Heads": sample_proportions,
        }
    )
    st.dataframe(
        results.tail(display_count),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Proportion Heads": st.column_config.NumberColumn(
                "Proportion Heads",
                format="%.3f",
            )
        },
    )
    if sample_count > display_count:
        st.caption(f"Showing the most recent {display_count:,} samples.")
