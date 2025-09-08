import os
import json
from openai import OpenAI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning("dotenv package not found. Make sure to set environment variables manually.")

# Initialize OpenAI client
# It's crucial to have OPENAI_API_KEY set in your environment
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
except Exception as e:
    logging.error(f"Failed to initialize OpenAI client: {e}")
    client = None

def extract_json_from_string(s: str):
    """
    Safely extracts the first valid JSON object from a string.
    Handles cases where the JSON is embedded within other text.
    """
    try:
        start_index = s.find('{')
        end_index = s.rfind('}') + 1
        if start_index != -1 and end_index != -1:
            json_str = s[start_index:end_index]
            return json.loads(json_str)
    except (json.JSONDecodeError, ValueError) as e:
        logging.error(f"JSON decoding failed: {e}")
        return None
    return None

def generate_questions(role: str, num_questions: int = 5) -> list:
    """
    Generates a list of interview questions for a given role using an LLM.

    Args:
        role (str): The job role for which to generate questions.
        num_questions (int): The number of questions to generate.

    Returns:
        list: A list of dictionaries, where each dictionary is a question.
              Returns a static list from questions.json on failure.
    """
    if not client:
        logging.error("OpenAI client not initialized. Falling back to static questions.")
        return load_static_questions()

    prompt = f"""
    You are an expert HR interviewer. Generate {num_questions} diverse interview questions for a candidate applying for the role of '{role}'.
    The questions should cover a range of topics, including technical skills, behavioral aspects, problem-solving abilities, and cultural fit.
    Return the output as a clean JSON array of objects, where each object has a single key "text" containing the question.

    Example format:
    [
        {{"text": "What is your experience with Python and Django?"}},
        {{"text": "Describe a time you had a conflict with a team member and how you resolved it."}}
    ]
    """

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"} # Use JSON mode if available
        )
        content = response.choices[0].message.content
        # The content should already be a JSON object, but we handle cases where it might be wrapped.
        questions_data = json.loads(content)
        # The prompt asks for an array, but the model might return a dictionary with a key.
        # We need to find the list of questions within the returned object.
        if isinstance(questions_data, dict):
            for key, value in questions_data.items():
                if isinstance(value, list):
                    return value # Return the first list found
        elif isinstance(questions_data, list):
             return questions_data

        logging.error("LLM returned unexpected JSON structure. Falling back to static questions.")
        return load_static_questions()

    except Exception as e:
        logging.error(f"Error generating questions with LLM: {e}")
        return load_static_questions()

def evaluate_answer(question: str, answer: str) -> dict:
    """
    Evaluates a candidate's answer to a question using an LLM.

    Args:
        question (str): The interview question that was asked.
        answer (str): The candidate's transcribed answer.

    Returns:
        dict: A dictionary containing the score, feedback, and a suggested better answer.
    """
    if not client or not answer:
        return {"score": 0, "feedback": "Evaluation could not be performed.", "better_answer": "N/A"}

    prompt = f"""
    As an expert interviewer, evaluate the following answer to an interview question.
    Provide a constructive, encouraging, and brief feedback.
    Also, provide a score from 0 to 10, where 0 is very poor and 10 is excellent.
    Finally, provide an improved, concise version of the answer that would be considered ideal.

    Question: "{question}"
    Candidate's Answer: "{answer}"

    Return your evaluation as a clean JSON object with three keys: "score", "feedback", and "better_answer".
    Example format:
    {{
        "score": 8,
        "feedback": "This is a strong answer that clearly demonstrates your skills. You could make it even better by providing a more specific metric of your success.",
        "better_answer": "In my previous role, I led a project that increased user engagement by 15% in one quarter by implementing a new recommendation algorithm."
    }}
    """
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        evaluation = json.loads(content)
        return evaluation
    except Exception as e:
        logging.error(f"Error evaluating answer with LLM: {e}")
        return {"score": 0, "feedback": "An error occurred during evaluation.", "better_answer": "Could not be generated."}


def get_interview_summary(evaluations: list) -> dict:
    """
    Generates a final summary of the interview based on all evaluations.

    Args:
        evaluations (list): A list of evaluation dictionaries for each answer.

    Returns:
        dict: A dictionary containing the final score and a summary paragraph.
    """
    if not client or not evaluations:
        return {"final_score": 0, "summary": "Could not generate a summary."}

    # Calculate average score
    total_score = sum(e.get('score', 0) for e in evaluations)
    num_questions = len(evaluations)
    final_score = round(total_score / num_questions, 1) if num_questions > 0 else 0

    # Prepare context for summary generation
    transcript = "\n\n".join(
        f"Question {i+1}: {e['question']}\nAnswer: {e['answer']}\nFeedback: {e['feedback']} (Score: {e['score']})"
        for i, e in enumerate(evaluations)
    )

    prompt = f"""
    Based on the following interview transcript and evaluations, provide a brief, overall summary of the candidate's performance.
    Highlight one key strength and one area for improvement. Keep the tone professional and constructive.
    Do not mention the final score in your summary text.

    Transcript:
    {transcript}

    Return a single JSON object with the key "summary".
    """

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        summary_data = json.loads(content)
        return {"final_score": final_score, "summary": summary_data.get("summary", "Summary could not be generated.")}

    except Exception as e:
        logging.error(f"Error generating summary with LLM: {e}")
        return {"final_score": final_score, "summary": "An error occurred while generating the final summary."}

def load_static_questions() -> list:
    """Loads the fallback questions from the local JSON file."""
    try:
        with open("questions.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # A hardcoded ultimate fallback
        return [{"text": "Tell me about yourself."}]
