import openai
import pandas as pd
import io
import os
from dotenv import load_dotenv
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, filename="app.log", format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not openai.api_key:
    raise ValueError("OpenAI API key not set in environment variables.")

def evaluate_text_answer(answer, task):
    """Evaluate a text-based answer using OpenAI."""
    prompt = (
        f"You are a strict but fair Excel interviewer. Question: {task['question']} | "
        f"Expected Answer: {task['expected_answer']} | Candidate Answer: {answer}. "
        f"Provide a score (0-10) in the format 'Score: X/10' and short feedback."
    )
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a strict but fair Excel interviewer."},
                {"role": "user", "content": prompt}
            ]
        )
        feedback = response["choices"][0]["message"]["content"]
        # Extract score from feedback
        match = re.search(r"Score: (\d+)/10", feedback)
        score = int(match.group(1)) if match else 5  # Default to 5 if no score found
        logging.info("Text answer evaluated. Score: %d, Feedback: %s", score, feedback)
        return score, feedback
    except openai.error.OpenAIError as e:
        logging.error("OpenAI API error: %s", str(e))
        return 0, f"Error evaluating answer: {str(e)}"
    except Exception as e:
        logging.error("Unexpected error in evaluate_text_answer: %s", str(e))
        return 0, f"Unexpected error: {str(e)}"

def evaluate_excel_answer(file, task):
    """Evaluate an uploaded Excel file."""
    try:
        if "expected_column" not in task:
            logging.warning("Missing expected_column in task: %s", task['question'])
            return 0, "Task configuration missing 'expected_column'."
        
        df = pd.read_excel(file)
        expected_column = task["expected_column"]
        
        # Check if expected column exists
        if expected_column not in df.columns:
            logging.warning("Expected column '%s' not found in uploaded file", expected_column)
            return 5, f"Expected column '{expected_column}' not found."
        
        # Additional validation (example: check if column has non-null values)
        if df[expected_column].isna().all():
            logging.warning("Column '%s' is empty in uploaded file", expected_column)
            return 7, f"Column '{expected_column}' found but contains no data."
        
        logging.info("Excel file evaluated successfully for column '%s'", expected_column)
        return 10, f"Correct column '{expected_column}' found with valid data."
    except Exception as e:
        logging.error("Error evaluating Excel file: %s", str(e))
        return 0, f"Error reading Excel file: {str(e)}"
