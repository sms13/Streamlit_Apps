import random
import json
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


DEFAULT_CHALLENGE_TARGET = 20
LEADERBOARD_FILE = Path(__file__).with_name("leaderboard.json")


def next_card() -> tuple[int, int]:
    return random.randint(1, 10), random.randint(1, 10)


def initialize_state() -> None:
    if "current_card" not in st.session_state:
        st.session_state.current_card = next_card()
    if "correct_count" not in st.session_state:
        st.session_state.correct_count = 0
    if "attempt_count" not in st.session_state:
        st.session_state.attempt_count = 0
    if "streak" not in st.session_state:
        st.session_state.streak = 0
    if "feedback" not in st.session_state:
        st.session_state.feedback = ""
    if "history" not in st.session_state:
        st.session_state.history = []
    if "game_active" not in st.session_state:
        st.session_state.game_active = False
    if "game_correct" not in st.session_state:
        st.session_state.game_correct = 0
    if "game_attempts" not in st.session_state:
        st.session_state.game_attempts = 0
    if "game_start_time" not in st.session_state:
        st.session_state.game_start_time = None
    if "game_elapsed" not in st.session_state:
        st.session_state.game_elapsed = None
    if "game_results" not in st.session_state:
        st.session_state.game_results = []
    if "show_balloons" not in st.session_state:
        st.session_state.show_balloons = False
    if "challenge_player_name" not in st.session_state:
        st.session_state.challenge_player_name = ""
    if "game_player_name" not in st.session_state:
        st.session_state.game_player_name = ""
    if "selected_challenge_target" not in st.session_state:
        st.session_state.selected_challenge_target = DEFAULT_CHALLENGE_TARGET
    if "game_target" not in st.session_state:
        st.session_state.game_target = DEFAULT_CHALLENGE_TARGET
    if "challenge_leaderboards" not in st.session_state:
        st.session_state.challenge_leaderboards = load_leaderboards()


def reset_session() -> None:
    st.session_state.current_card = next_card()
    st.session_state.correct_count = 0
    st.session_state.attempt_count = 0
    st.session_state.streak = 0
    st.session_state.feedback = ""
    st.session_state.history = []
    st.session_state.game_active = False
    st.session_state.game_correct = 0
    st.session_state.game_attempts = 0
    st.session_state.game_start_time = None
    st.session_state.game_elapsed = None
    st.session_state.game_results = []
    st.session_state.show_balloons = False
    st.session_state.game_player_name = ""


def load_leaderboards() -> dict[str, list[dict[str, int | str | float]]]:
    if not LEADERBOARD_FILE.exists():
        return {}

    try:
        with LEADERBOARD_FILE.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}

    if not isinstance(data, dict):
        return {}

    valid_leaderboards: dict[str, list[dict[str, int | str | float]]] = {}
    for target, entries in data.items():
        if not isinstance(target, str) or not isinstance(entries, list):
            continue

        cleaned_entries: list[dict[str, int | str | float]] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            if {
                "name",
                "elapsed_seconds",
                "time",
                "questions_asked",
            }.issubset(entry.keys()):
                cleaned_entries.append(entry)

        valid_leaderboards[target] = cleaned_entries[:5]

    return valid_leaderboards


def save_leaderboards() -> None:
    try:
        with LEADERBOARD_FILE.open("w", encoding="utf-8") as handle:
            json.dump(st.session_state.challenge_leaderboards, handle, indent=2)
    except OSError:
        pass


def current_challenge_target() -> int:
    if st.session_state.game_active:
        return st.session_state.game_target
    return st.session_state.selected_challenge_target


def start_game() -> None:
    st.session_state.current_card = next_card()
    st.session_state.feedback = ""
    st.session_state.game_active = True
    st.session_state.game_correct = 0
    st.session_state.game_attempts = 0
    st.session_state.game_start_time = time.time()
    st.session_state.game_elapsed = None
    st.session_state.show_balloons = False
    st.session_state.game_target = st.session_state.selected_challenge_target
    st.session_state.game_player_name = st.session_state.challenge_player_name.strip()


def format_elapsed(seconds: float) -> str:
    total_centiseconds = max(0, int(seconds * 100))
    minutes = total_centiseconds // 6000
    secs = (total_centiseconds % 6000) // 100
    hundredths = total_centiseconds % 100
    return f"{minutes:02d}:{secs:02d}.{hundredths:02d}"


def record_challenge_result(
    target: int,
    player_name: str,
    elapsed_seconds: float,
    questions_asked: int,
) -> None:
    leaderboard = st.session_state.challenge_leaderboards.get(str(target), [])
    display_name = player_name.strip() or "Anonymous"
    leaderboard.append(
        {
            "name": display_name,
            "elapsed_seconds": elapsed_seconds,
            "time": format_elapsed(elapsed_seconds),
            "questions_asked": questions_asked,
        }
    )
    leaderboard.sort(
        key=lambda entry: (
            entry["elapsed_seconds"],
            entry["questions_asked"],
            entry["name"].lower(),
        )
    )
    st.session_state.challenge_leaderboards[str(target)] = leaderboard[:5]
    save_leaderboards()


def leaderboard_rows(target: int) -> list[dict[str, str | int]]:
    leaderboard = st.session_state.challenge_leaderboards.get(str(target), [])
    rows: list[dict[str, str | int]] = []
    for index, entry in enumerate(leaderboard, start=1):
        rows.append(
            {
                "Rank": index,
                "Name": entry["name"],
                "Time": entry["time"],
                "Questions Asked": entry["questions_asked"],
            }
        )
    return rows


def submit_answer(student_answer: int, *, advance_card: bool = True) -> bool:
    first, second = st.session_state.current_card
    correct_answer = first * second
    is_correct = student_answer == correct_answer

    st.session_state.attempt_count += 1

    if is_correct:
        st.session_state.correct_count += 1
        st.session_state.streak += 1
        st.session_state.feedback = (
            f"Correct. {first} x {second} = {correct_answer}."
        )
    else:
        st.session_state.streak = 0
        st.session_state.feedback = (
            f"Not quite. {first} x {second} = {correct_answer}."
        )

    st.session_state.history = [
        {
            "problem": f"{first} x {second}",
            "your_answer": student_answer,
            "correct_answer": correct_answer,
            "result": "Correct" if is_correct else "Try again",
        },
        *st.session_state.history,
    ][:8]

    if advance_card:
        st.session_state.current_card = next_card()
    return is_correct


st.set_page_config(page_title="Multiplication Flash Cards", page_icon="x", layout="centered")

st.markdown(
    """
    <style>
    div.block-container {
        padding-top: 1.2rem;
    }
    div[data-testid="stTextInput"] input {
        font-size: 2rem;
        padding: 0.9rem 1rem;
    }
    div[data-testid="stNumberInput"] input {
        font-size: 2rem;
        padding: 0.9rem 1rem;
    }
    div[data-testid="stRadio"] > label p {
        font-size: 1.35rem !important;
        font-weight: 800 !important;
    }
    div[data-testid="stNumberInput"] > label p {
        font-size: 1.35rem !important;
        font-weight: 800 !important;
    }
    div[data-testid="stTextInput"] > label p {
        font-size: 1.35rem !important;
        font-weight: 800 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label p {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="stButton"] > button {
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.01em;
        min-height: 3rem;
    }
    div[data-testid="stButton"] > button p,
    div[data-testid="stButton"] > button span {
        font-size: 1.35rem !important;
        font-weight: 800 !important;
    }
    div[data-testid="stButton"] > button[kind="primary"] {
        background: #1f8f4d !important;
        border-color: #1f8f4d !important;
        color: white !important;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: #18713d !important;
        border-color: #18713d !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

initialize_state()

if st.session_state.show_balloons:
    st.balloons()
    st.session_state.show_balloons = False

st.title("10 x 10 Multiplication Flash Cards")
st.caption("Practice multiplication facts from 1 x 1 through 10 x 10.")
mode = st.radio(
    "Mode",
    ["Practice", "Time Challenge"],
    horizontal=True,
    key="mode_select",
)

left_col, right_col = st.columns([2, 1])

challenge_finished = (
    mode == "Time Challenge"
    and not st.session_state.game_active
    and st.session_state.game_elapsed is not None
    and st.session_state.game_correct >= st.session_state.game_target
)

with left_col:
    if mode == "Time Challenge":
        st.number_input(
            "Correct answers needed",
            min_value=1,
            max_value=100,
            step=1,
            value=DEFAULT_CHALLENGE_TARGET,
            key="selected_challenge_target",
            disabled=st.session_state.game_active,
        )

        st.text_input(
            "Player name (optional)",
            placeholder="Enter your name",
            key="challenge_player_name",
            disabled=st.session_state.game_active,
        )

        if st.button(
            "Start Time Challenge",
            use_container_width=True,
            type="primary",
        ):
            start_game()
            st.rerun()

        with st.container(border=True):
            if st.session_state.game_active and st.session_state.game_start_time is not None:
                start_ms = int(st.session_state.game_start_time * 1000)
                components.html(
                    f"""
                    <div id="live-stopwatch" style="font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 1.8rem; font-weight: 700;">00:00.00</div>
                    <script>
                    const startMs = {start_ms};
                    const node = document.getElementById("live-stopwatch");

                    function pad(n) {{
                        return String(n).padStart(2, "0");
                    }}

                    function render() {{
                        const nowMs = Date.now();
                        const elapsedMs = Math.max(0, nowMs - startMs);
                        const totalCentiseconds = Math.floor(elapsedMs / 10);
                        const minutes = Math.floor(totalCentiseconds / 6000);
                        const seconds = Math.floor((totalCentiseconds % 6000) / 100);
                        const hundredths = totalCentiseconds % 100;
                        node.textContent = `${{pad(minutes)}}:${{pad(seconds)}}.${{pad(hundredths)}}`;
                    }}

                    render();
                    setInterval(render, 50);
                    </script>
                    """,
                    height=56,
                )
            elif st.session_state.game_elapsed is not None:
                st.metric("Time", format_elapsed(st.session_state.game_elapsed))
            else:
                st.metric("Time", "00:00.00")

    if not challenge_finished:
        first, second = st.session_state.current_card
        st.markdown(
            f"<div style='font-size: 4rem; font-weight: 700; text-align: center; padding: 0.2rem 0 0.8rem 0;'>{first} x {second} = ?</div>",
            unsafe_allow_html=True,
        )

        with st.form("flash_card_form", clear_on_submit=True):
            st.subheader("Answer")
            student_answer = st.text_input(
                "Answer",
                value="",
                placeholder="Type a number",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Check answer")
            if submitted:
                if mode == "Time Challenge" and not st.session_state.game_active:
                    st.session_state.feedback = "Start the game first."
                    st.rerun()

                cleaned_answer = student_answer.strip()
                if cleaned_answer.isdigit() and 0 <= int(cleaned_answer) <= 100:
                    answer_value = int(cleaned_answer)
                    final_challenge_answer = (
                        mode == "Time Challenge"
                        and st.session_state.game_active
                        and st.session_state.game_correct
                        == st.session_state.game_target - 1
                        and answer_value == first * second
                    )
                    is_correct = submit_answer(
                        answer_value,
                        advance_card=not final_challenge_answer,
                    )

                    if mode == "Time Challenge" and st.session_state.game_active:
                        st.session_state.game_attempts += 1
                        if is_correct:
                            st.session_state.game_correct += 1

                        if st.session_state.game_correct >= st.session_state.game_target:
                            st.session_state.game_active = False
                            if st.session_state.game_start_time is not None:
                                st.session_state.game_elapsed = (
                                    time.time() - st.session_state.game_start_time
                                )
                            final_time = format_elapsed(st.session_state.game_elapsed or 0)
                            final_attempts = st.session_state.game_attempts
                            record_challenge_result(
                                st.session_state.game_target,
                                st.session_state.game_player_name,
                                st.session_state.game_elapsed or 0,
                                final_attempts,
                            )
                            st.session_state.feedback = (
                                "Challenge complete! "
                                f"{st.session_state.game_target} correct in {final_time}. "
                                f"Questions asked: {final_attempts}."
                            )
                            st.session_state.show_balloons = True

                    st.rerun()
                else:
                    st.session_state.feedback = "Enter a whole number from 0 to 100."

    if st.session_state.feedback:
        if st.session_state.feedback.startswith(("Correct", "Challenge complete!")):
            st.success(st.session_state.feedback)
        else:
            st.warning(st.session_state.feedback)

with right_col:
    accuracy = 0
    if st.session_state.attempt_count:
        accuracy = round(
            100 * st.session_state.correct_count / st.session_state.attempt_count
        )

    st.metric("Correct", st.session_state.correct_count)
    st.metric("Tried", st.session_state.attempt_count)
    st.metric("Accuracy", f"{accuracy}%")
    st.metric("Streak", st.session_state.streak)

    if mode == "Time Challenge":
        active_target = current_challenge_target()
        st.metric(
            "Number correct",
            f"{st.session_state.game_correct}/{active_target}",
        )
        st.metric("Question Attempts", st.session_state.game_attempts)

        if st.session_state.game_elapsed is not None:
            st.metric("Final Time", format_elapsed(st.session_state.game_elapsed))
            st.metric("Questions Asked", st.session_state.game_attempts)

    if st.button("Start over", use_container_width=True):
        reset_session()
        st.rerun()

st.divider()
if mode == "Time Challenge":
    st.subheader("Leaderboard")

    leaderboard = leaderboard_rows(current_challenge_target())
    if leaderboard:
        st.table(leaderboard)
    else:
        st.caption("Top 5 fastest times for this target will appear here.")

    st.divider()

st.subheader("Recent cards")

if st.session_state.history:
    st.table(st.session_state.history)
else:
    st.write("Answer a few cards to see recent results here.")
