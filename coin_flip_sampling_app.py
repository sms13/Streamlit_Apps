import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Coin Flipping", layout="wide")


st.html("""
<style>
.st-key-active_coin_tab [role="tablist"] {
    gap: 12px;
    border-bottom: 2px solid #91a8aa;
    padding: 4px 4px 0;
}
.st-key-active_coin_tab [role="tab"] {
    height: auto;
    min-height: 48px;
    padding: 12px 22px;
    border: 1px solid #91a8aa;
    border-bottom: 0;
    border-radius: 10px 10px 0 0;
    background: #edf2f3;
    color: #263f42;
}
.st-key-active_coin_tab [role="tab"] p {
    font-weight: 600;
}
.st-key-active_coin_tab [role="tab"]:hover {
    background: #dce9ea;
}
.st-key-active_coin_tab [role="tab"][aria-selected="true"] {
    background: #2f6f73;
    color: white;
    border-color: #2f6f73;
}
.st-key-active_coin_tab [role="tab"]:focus-visible {
    outline: 3px solid #d99532;
    outline-offset: 2px;
}
.st-key-active_coin_tab [data-baseweb="tab-highlight"] {
    display: none;
}
</style>
""")


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


def generate_lln_trend(p_heads: float) -> np.ndarray:
    sample_sizes = np.arange(50, 10_001, 50)
    return np.random.binomial(sample_sizes, p_heads) / sample_sizes


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

clt_tab, lln_tab = st.tabs([
    "The Central Limit Theorem: Coin Flipping",
    "The Law of Large Numbers: Coin Flipping",
], key="active_coin_tab", on_change="rerun")

active_sample_key = "lln_sample_size" if lln_tab.open else "clt_sample_size"

with st.sidebar:
    st.header("Simulation Settings")
    flips_per_sample = st.number_input(
        "Flips per sample",
        min_value=1,
        max_value=10_000,
        value=st.session_state.get(active_sample_key, 100),
        key=f"{active_sample_key}_input",
        step=1,
        help="Each simulation records the proportion of heads in this many flips.",
    )
    st.session_state[active_sample_key] = int(flips_per_sample)
    p_heads = st.slider(
        "True probability of heads",
        min_value=0.0,
        max_value=1.0,
        value=0.50,
        step=0.01,
    )





flip_again = False
show_growth = st.session_state.get("lln_show_growth", False)
if lln_tab.open:
    with st.sidebar:
        flip_again = st.button("Flip this many again", use_container_width=True)
        show_growth = st.session_state.get("lln_show_growth", False)
        if st.button(
            "Hide sample proportion trend" if show_growth
            else "Show sample proportion as the number of flips grows",
            key="lln_view_button",
            use_container_width=True,
        ):
            show_growth = not show_growth
            st.session_state.lln_show_growth = show_growth
            if show_growth:
                st.session_state.lln_trend_proportions = generate_lln_trend(float(p_heads))
                st.session_state.lln_trend_probability = float(p_heads)
                st.session_state.lln_trend_independent = True
            st.rerun()

if clt_tab.open:
    with st.sidebar:
        st.button("Reset sampling distribution", on_click=reset_simulation, use_container_width=True)

with clt_tab:
    flips_per_sample = st.session_state.get("clt_sample_size", 100)
    st.title("The Central Limit Theorem: Coin Flipping")
    st.caption(
        "Simulate repeated samples of coin flips and watch the sampling distribution "
        "of the sample proportion of heads take shape."
    )

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


with lln_tab:
    flips_per_sample = st.session_state.get("lln_sample_size", 100)
    st.title("The Law of Large Numbers: Coin Flipping")
    st.caption(
        "Compare the sample proportion of heads with the true proportion. "
        "Change flips per sample to automatically generate a fresh sample."
    )
    lln_settings = (int(flips_per_sample), float(p_heads))
    if st.session_state.get("lln_settings") != lln_settings or flip_again:
        st.session_state.lln_flips = np.random.binomial(
            1, float(p_heads), size=int(flips_per_sample)
        )
        st.session_state.lln_settings = lln_settings

    flips = st.session_state.lln_flips
    sample_proportion = float(np.mean(flips))

    metrics = st.columns(3)
    metrics[0].metric("Flips in sample", f"{len(flips):,}")
    metrics[1].metric("Sample proportion of heads", f"{sample_proportion:.3f}")
    metrics[2].metric("True proportion of heads", f"{p_heads:.2f}")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axvline(
        float(p_heads),
        color="#B23A48",
        linestyle="-",
        linewidth=2,
        label=f"True proportion = {p_heads:.2f}",
    )
    ax.axvline(
        sample_proportion,
        color="#2F6F73",
        linestyle=":",
        linewidth=2,
        label=f"Sample proportion = {sample_proportion:.3f}",
    )
    ax.set_xlim(-0.02, 1.02)
    ax.set_xlabel("Sample proportion of heads")
    ax.set_title("Sample Proportion Compared with the True Proportion")
    ax.yaxis.set_visible(False)
    for side in ("left", "right", "top"):
        ax.spines[side].set_visible(False)
    ax.legend()
    fig.tight_layout()
    st.pyplot(fig, width=1000)
    plt.close(fig)

    if show_growth:
        if (
            st.session_state.get("lln_trend_probability") != float(p_heads)
            or not st.session_state.get("lln_trend_independent", False)
            or len(st.session_state.get("lln_trend_proportions", [])) != 200
        ):
            st.session_state.lln_trend_proportions = generate_lln_trend(float(p_heads))
            st.session_state.lln_trend_probability = float(p_heads)
            st.session_state.lln_trend_independent = True
        trend_size = 50 * len(st.session_state.lln_trend_proportions)
        flip_numbers = np.arange(50, trend_size + 1, 50)
        sample_proportions = st.session_state.lln_trend_proportions
        st.caption(
            f"Each point uses a fresh, independent sample of n flips, with n increasing by 50 through {trend_size:,}. "
            "Hide and show the trend to generate a fresh set of samples."
        )
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(
            flip_numbers,
            sample_proportions,
            color="#2F6F73",
            linestyle="-",
            linewidth=1.5,
            marker="o",
            markersize=4,
            label="Sample proportion of heads (fresh sample at each n)",
        )
        ax.axhline(
            float(p_heads),
            color="#B23A48",
            linestyle="-",
            linewidth=2,
            label=f"True proportion = {p_heads:.2f}",
        )
        ax.set_xlim(0, trend_size)
        ax.set_ylim(float(p_heads) - 0.1, float(p_heads) + 0.1)
        ax.set_xlabel("Number of flips")
        ax.set_ylabel("Proportion of heads")
        ax.set_title("Sample Proportion as the Number of Flips Grows")
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()
        st.pyplot(fig, width=1000)
        plt.close(fig)
