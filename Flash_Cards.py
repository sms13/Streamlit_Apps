import random
import time

import streamlit as st
import streamlit.components.v1 as components


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


def start_game() -> None:
    st.session_state.current_card = next_card()
    st.session_state.feedback = ""
    st.session_state.game_active = True
    st.session_state.game_correct = 0
    st.session_state.game_attempts = 0
    st.session_state.game_start_time = time.time()
    st.session_state.game_elapsed = None


def format_elapsed(seconds: float) -> str:
    total_centiseconds = max(0, int(seconds * 100))
    minutes = total_centiseconds // 6000
    secs = (total_centiseconds % 6000) // 100
    hundredths = total_centiseconds % 100
    return f"{minutes:02d}:{secs:02d}.{hundredths:02d}"


def submit_answer(student_answer: int) -> bool:
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
    div[data-testid="stRadio"] > label p {
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
    </style>
    """,
    unsafe_allow_html=True,
)

initialize_state()

st.title("10 x 10 Multiplication Flash Cards")
st.caption("Practice multiplication facts from 1 x 1 through 10 x 10.")
mode = st.radio(
    "Mode",
    ["Practice", "20 Correct Challenge"],
    horizontal=True,
    key="mode_select",
)

left_col, right_col = st.columns([2, 1])

with left_col:
    if mode == "20 Correct Challenge":
        if st.button("Start 20-Correct Game", use_container_width=True):
            start_game()
            st.rerun()

        with st.container(border=True):
            st.markdown("**Stopwatch**")
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
            if mode == "20 Correct Challenge" and not st.session_state.game_active:
                st.session_state.feedback = "Start the game first."
                st.rerun()

            cleaned_answer = student_answer.strip()
            if cleaned_answer.isdigit() and 0 <= int(cleaned_answer) <= 100:
                is_correct = submit_answer(int(cleaned_answer))

                if mode == "20 Correct Challenge" and st.session_state.game_active:
                    st.session_state.game_attempts += 1
                    if is_correct:
                        st.session_state.game_correct += 1

                    if st.session_state.game_correct >= 20:
                        st.session_state.game_active = False
                        if st.session_state.game_start_time is not None:
                            st.session_state.game_elapsed = (
                                time.time() - st.session_state.game_start_time
                            )
                        final_time = format_elapsed(st.session_state.game_elapsed or 0)
                        final_attempts = st.session_state.game_attempts
                        st.session_state.game_results = [
                            {
                                "time": final_time,
                                "questions_asked": final_attempts,
                            },
                            *st.session_state.game_results,
                        ][:10]
                        st.session_state.feedback = (
                            "Challenge complete! "
                            f"Time: {final_time}. Questions asked: {final_attempts}."
                        )

                st.rerun()
            else:
                st.session_state.feedback = "Enter a whole number from 0 to 100."

    if st.session_state.feedback:
        if st.session_state.feedback.startswith("Correct"):
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

    if mode == "20 Correct Challenge":
        st.metric("Number correct", st.session_state.game_correct)
        st.metric("Question Attempts", st.session_state.game_attempts)

        if st.session_state.game_elapsed is not None:
            st.metric("Final Time", format_elapsed(st.session_state.game_elapsed))
            st.metric("Questions Asked", st.session_state.game_attempts)

    if st.button("Start over", use_container_width=True):
        reset_session()
        st.rerun()

st.divider()
st.subheader("Recent cards")

if st.session_state.history:
    st.table(st.session_state.history)
else:
    st.write("Answer a few cards to see recent results here.")

if mode == "20 Correct Challenge" and st.session_state.game_results:
    st.subheader("Challenge results")
    st.table(st.session_state.game_results)
