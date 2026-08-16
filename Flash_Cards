import random

import streamlit as st


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


def reset_session() -> None:
    st.session_state.current_card = next_card()
    st.session_state.correct_count = 0
    st.session_state.attempt_count = 0
    st.session_state.streak = 0
    st.session_state.feedback = ""
    st.session_state.history = []


def submit_answer(student_answer: int) -> None:
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


st.set_page_config(page_title="Multiplication Flash Cards", page_icon="x", layout="centered")

initialize_state()

st.title("10 x 10 Multiplication Flash Cards")
st.caption("Practice multiplication facts from 1 x 1 through 10 x 10.")

left_col, right_col = st.columns([2, 1])

with left_col:
    first, second = st.session_state.current_card
    st.subheader("Solve this card")
    st.markdown(
        f"<div style='font-size: 4rem; font-weight: 700; text-align: center; padding: 1rem 0;'>{first} x {second} = ?</div>",
        unsafe_allow_html=True,
    )

    with st.form("flash_card_form", clear_on_submit=True):
        student_answer = st.number_input(
            "Student answer",
            min_value=0,
            max_value=100,
            step=1,
        )
        submitted = st.form_submit_button("Check answer")
        if submitted:
            submit_answer(student_answer)
            st.rerun()

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

    if st.button("Start over", use_container_width=True):
        reset_session()
        st.rerun()

st.divider()
st.subheader("Recent cards")

if st.session_state.history:
    st.table(st.session_state.history)
else:
    st.write("Answer a few cards to see recent results here.")
