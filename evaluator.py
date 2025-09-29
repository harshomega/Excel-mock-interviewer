import openai
import pandas as pd
import io

# Load your API key
openai.api_key = ""
def evaluate_text_answer(answer, task):
    prompt = f"You are a Python interviewer. Question: {task['question']} | Candidate Answer: {answer}. Provide a score (0-10) and short feedback."
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a strict but fair Excel interviewer."},
                  {"role": "user", "content": prompt}]
    )
    feedback = response["choices"][0]["message"]["content"]
    # For PoC, simulate scoring
    score = min(len(answer) // 10, 10)
    return score, feedback

def evaluate_excel_answer(file, task):
    df = pd.read_excel(file)
    # Example check: does the sheet contain a formula result column?
    if task.get("expected_column") in df.columns:
        return 10, "Correct column found!"
    else:
        return 5, "Column not found, partial credit."
