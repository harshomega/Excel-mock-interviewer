import streamlit as st
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, filename="app.log", format="%(asctime)s - %(levelname)s - %(message)s")

# Load tasks using relative path
BASE_DIR = os.path.dirname(__file__)
TASKS_FILE = os.path.join(BASE_DIR, "sample_task.json")

try:
    with open(TASKS_FILE) as f:
        tasks = json.load(f).get("tasks", [])
except FileNotFoundError:
    st.error("Error: Task file not found.")
    logging.error("Task file not found: %s", TASKS_FILE)
    st.stop()
except json.JSONDecodeError:
    st.error("Error: Invalid JSON format in task file.")
    logging.error("Invalid JSON in task file: %s", TASKS_FILE)
    st.stop()

st.title("AI-Powered Excel Mock Interviewer")

st.markdown("""
Welcome! I will act as your Excel interviewer. You'll be asked a few questions
about Excel concepts and practical tasks. At the end, you'll get a performance summary.
""")

# Initialize session state
if "responses" not in st.session_state:
    st.session_state.responses = []

# Reset button
if st.button("Reset Interview"):
    st.session_state.responses = []
    st.success("Interview reset.")
    logging.info("Interview session reset by user.")

for i, task in enumerate(tasks):
    # Validate task type
    task_type = task.get("type")
    if task_type not in ["text", "excel"]:
        st.error(f"Invalid task type for question {i+1}: {task_type}")
        logging.warning("Invalid task type for question %d: %s", i+1, task_type)
        continue

    st.subheader(f"Q{i+1}. {task['question']}")

    if task_type == "text":
        answer = st.text_area("Your Answer", key=f"q{i}", height=150)
        if answer:
            # Check for existing response to avoid duplicates
            if not any(r["q"] == task["question"] for r in st.session_state.responses):
                from evaluator import evaluate_text_answer
                try:
                    score, feedback = evaluate_text_answer(answer, task)
                    st.session_state.responses.append({
                        "q": task['question'],
                        "ans": answer,
                        "score": score,
                        "feedback": feedback
                    })
                    st.success(f"Score: {score}/10 | Feedback: {feedback}")
                    logging.info("Text answer submitted for question %d: Score=%d", i+1, score)
                except Exception as e:
                    st.error(f"Error evaluating answer: {str(e)}")
                    logging.error("Error evaluating text answer for question %d: %s", i+1, str(e))

    elif task_type == "excel":
        st.write(f"Instructions: Upload an Excel file containing the column '{task.get('expected_column', 'unknown')}'.")
        file = st.file_uploader("Upload Excel file", type=["xlsx"], key=f"q{i}")
        if file:
            # Validate file size (limit to 10MB)
            MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
            if file.size > MAX_FILE_SIZE:
                st.error("File size exceeds 10MB limit.")
                logging.warning("File size too large for question %d: %d bytes", i+1, file.size)
            else:
                # Check for existing response
                if not any(r["q"] == task["question"] for r in st.session_state.responses):
                    from evaluator import evaluate_excel_answer
                    try:
                        score, feedback = evaluate_excel_answer(file, task)
                        st.session_state.responses.append({
                            "q": task['question'],
                            "ans": "Excel file uploaded",
                            "score": score,
                            "feedback": feedback
                        })
                        st.success(f"Score: {score}/10 | Feedback: {feedback}")
                        logging.info("Excel answer submitted for question %d: Score=%d", i+1, score)
                    except Exception as e:
                        st.error(f"Error evaluating Excel file: {str(e)}")
                        logging.error("Error evaluating Excel file for question %d: %s", i+1, str(e))

if st.button("Finish Interview"):
    st.header("Final Report")
    if st.session_state.responses:
        total_score = sum(r["score"] for r in st.session_state.responses) / len(st.session_state.responses)
        st.write(f"Overall Score: {total_score:.2f}/10")
        logging.info("Interview completed. Overall score: %.2f", total_score)
        for r in st.session_state.responses:
            st.write(f"- Q: {r['q']} | Score: {r['score']}/10 | Feedback: {r['feedback']}")
    else:
        st.write("No responses submitted.")
        logging.info("Interview finished with no responses.")
