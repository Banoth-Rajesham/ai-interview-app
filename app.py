import os
import gradio as gr
from interview import generate_questions, evaluate_answer, summarize_interview
from pdf_report import generate_pdf
import time

# State helpers
def init_state():
    return {
        "candidate_name":"",
        "role":"",
        "resume_text":"",
        "questions":[],
        "answers":[],
        "current_q":0,
        "start_time":None
    }

state = init_state()

# Resume reading
def read_resume(file_obj):
    try:
        import PyPDF2
        if file_obj.name.endswith(".pdf"):
            reader = PyPDF2.PdfReader(file_obj)
            return "\n".join([page.extract_text() or "" for page in reader.pages])
        return file_obj.read().decode("utf-8")
    except Exception:
        return ""

# Setup interview
def start_interview(candidate_name, role, resume_file, num_questions):
    state["candidate_name"] = candidate_name
    state["role"] = role
    state["resume_text"] = read_resume(resume_file)
    state["questions"] = generate_questions(state["resume_text"], role, num_questions)
    state["answers"] = []
    state["current_q"] = 0
    state["start_time"] = time.time()
    return state["questions"], state["answers"]

# Submit answer
def submit_answer(candidate_answer):
    if state["current_q"] >= len(state["questions"]):
        return state["answers"]
    q_text = state["questions"][state["current_q"]]["text"]
    eval_result = evaluate_answer(q_text, candidate_answer, state["resume_text"])
    eval_result["answer"] = candidate_answer
    state["answers"].append(eval_result)
    state["current_q"] += 1
    return state["answers"]

# Generate report
def generate_report():
    summary = summarize_interview(state["questions"], state["answers"], state["resume_text"])
    pdf_bytes = generate_pdf(state["candidate_name"], state["role"], summary, state["questions"], state["answers"])
    return summary, pdf_bytes

# Timer display
def get_elapsed_time():
    if not state["start_time"]:
        return "00:00"
    elapsed = int(time.time() - state["start_time"])
    mins, secs = divmod(elapsed, 60)
    return f"{mins:02d}:{secs:02d}"

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# 🎯 AI Interview App (Production)")

    with gr.Tab("Setup"):
        candidate_name = gr.Textbox(label="Candidate Name")
        role = gr.Textbox(label="Job Role")
        resume_file = gr.File(label="Upload Resume (PDF/TXT)")
        num_questions = gr.Slider(3,10,value=5,step=1,label="Number of Questions")
        setup_btn = gr.Button("Start Interview")
        questions_output = gr.State()
        answers_output = gr.State()
        setup_btn.click(start_interview, inputs=[candidate_name, role, resume_file, num_questions],
                        outputs=[questions_output, answers_output])

    with gr.Tab("Answer Questions"):
        timer_display = gr.Label(label="Elapsed Time")
        current_question = gr.Textbox(label="Current Question")
        candidate_answer = gr.Textbox(label="Your Answer", lines=4)
        submit_btn = gr.Button("Submit Answer")
        submit_btn.click(submit_answer, inputs=[candidate_answer], outputs=[answers_output])
        gr.Label(get_elapsed_time, label="Timer (updates every sec)")

    with gr.Tab("Report"):
        report_btn = gr.Button("Generate PDF & Summary")
        summary_box = gr.Textbox(label="Interview Summary")
        pdf_download = gr.File(label="Download PDF")
        report_btn.click(generate_report, outputs=[summary_box, pdf_download])

demo.launch()
