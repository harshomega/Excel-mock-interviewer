import streamlit as st
import json
from evaluator import evaluate_text_answer, evaluate_excel_answer

# Load tasks
tasks = json.load(open(r"C:\Users\msi 1\Documents\Excel_interviewer\sample_task.json"))

st.title("AI-Powered Excel Mock Interviewer")

st.markdown("""
Welcome! I will act as your Excel interviewer. You'll be asked a few questions
about Excel concepts and practical tasks. At the end, you'll get a performance summary.
""")

if "responses" not in st.session_state:
    st.session_state.responses = []

for i, task in enumerate(tasks):
    st.subheader(f"Q{i+1}. {task['question']}")

    if task["type"] == "text":
        answer = st.text_area("Your Answer", key=f"q{i}")
        if answer:
            score, feedback = evaluate_text_answer(answer, task)
            st.session_state.responses.append({"q": task['question'], "ans": answer, "score": score, "feedback": feedback})
            st.success(f"Score: {score} | Feedback: {feedback}")

    elif task["type"] == "excel":
        file = st.file_uploader("Upload Excel file", type=["xlsx"], key=f"q{i}")
        if file:
            score, feedback = evaluate_excel_answer(file, task)
            st.session_state.responses.append({"q": task['question'], "ans": "Excel file uploaded", "score": score, "feedback": feedback})
            st.success(f"Score: {score} | Feedback: {feedback}")

if st.button("Finish Interview"):
    st.header("Final Report")
    total_score = sum([r["score"] for r in st.session_state.responses]) / len(st.session_state.responses)
    st.write(f"Overall Score: {total_score:.2f}")

    for r in st.session_state.responses:
        st.write(f"- Q: {r['q']} | Score: {r['score']} | Feedback: {r['feedback']}")