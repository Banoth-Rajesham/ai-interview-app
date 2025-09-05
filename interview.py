import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Stable JSON extraction
def extract_first_json_block(text: str):
    for open_char, close_char in [("{", "}"), ("[", "]")]:
        stack = []
        start_idx = None
        for i, ch in enumerate(text):
            if ch == open_char:
                if not stack:
                    start_idx = i
                stack.append(ch)
            elif ch == close_char and stack:
                stack.pop()
                if not stack and start_idx is not None:
                    candidate = text[start_idx:i+1]
                    try:
                        return json.loads(candidate)
                    except Exception:
                        continue
    return None

# Generate interview questions
def generate_questions(resume_text, role, num_questions=5):
    prompt = (
        f"Generate {num_questions} interview questions for a {role} "
        f"based on this resume:\n{resume_text}\n"
        "Return a JSON list of questions with fields: text, topic, difficulty."
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}]
        )
        content = resp.choices[0].message.content
        questions = extract_first_json_block(content)
        return questions or []
    except Exception as e:
        return []

# Evaluate candidate answer
def evaluate_answer(question, answer, resume):
    prompt = (
        f"Given the resume:\n{resume}\n"
        f"Evaluate the answer to the question:\n{question}\n"
        f"Candidate answer:\n{answer}\n"
        "Return a JSON: {score (1-10), feedback, better_answer}"
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}]
        )
        eval_json = extract_first_json_block(resp.choices[0].message.content)
        if not isinstance(eval_json, dict):
            return {"score":0,"feedback":"Evaluation failed","better_answer":""}
        return eval_json
    except Exception:
        return {"score":0,"feedback":"Error during evaluation","better_answer":""}

# Summarize interview
def summarize_interview(questions, answers, resume):
    transcript_parts = []
    for q, a in zip(questions, answers):
        transcript_parts.append(f"Q: {q.get('text','')}\nA: {a.get('answer','')}\nScore: {a.get('score',0)}/10")
    transcript = "\n\n".join(transcript_parts)
    prompt = (
        f"Summarize the interview based on resume:\n{resume}\n"
        f"Transcript:\n{transcript}\n"
        "Return JSON: {overall_score, strengths (list), weaknesses (list), recommendation}"
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}]
        )
        summary = extract_first_json_block(resp.choices[0].message.content)
        return summary or {}
    except Exception:
        return {}
