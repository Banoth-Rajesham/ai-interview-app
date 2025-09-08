import gradio as gr
import time
import logging

# Import utility functions from other modules
from llm_utils import generate_questions, evaluate_answer, get_interview_summary
from stt_utils import transcribe_audio
from tts_utils import speak_text

# Configure logging
logging.basicConfig(level=logging.INFO)

# --- State Management ---
def initialize_state():
    """Returns a dictionary representing the initial state of the interview."""
    return {
        "candidate_name": "",
        "role": "",
        "questions": [],
        "evaluations": [],
        "current_question_index": 0,
    }

# --- Core Interview Logic ---

def start_interview(name, role, num_questions):
    """
    Initializes the interview state, generates questions, and prepares the UI for the first question.
    """
    if not name or not role:
        # Show an error message if name or role is missing
        gr.Warning("Please enter both your name and the job role.")
        return None, None, gr.update(visible=True), gr.update(visible=False), gr.update(value=""), gr.update(value=None)
        
    logging.info(f"Starting interview for {name} for the role of {role}.")
    
    # Create a new state for the session
    state = initialize_state()
    state["candidate_name"] = name
    state["role"] = role
    
    # Generate questions using the LLM
    questions = generate_questions(role, int(num_questions))
    state["questions"] = questions
    
    if not questions:
        gr.Error("Failed to generate interview questions. Please try again.")
        return None, None, gr.update(visible=True), gr.update(visible=False), gr.update(value=""), gr.update(value=None)

    # Get the first question and its audio
    first_question_text = questions[0]['text']
    audio_path = speak_text(first_question_text)
    progress_text = f"Question 1 of {len(questions)}"

    # Update UI components: hide setup, show interview
    return state, gr.update(value=progress_text), gr.update(visible=False), gr.update(visible=True), gr.update(value=first_question_text), gr.update(value=audio_path)

def process_answer(state, audio_input):
    """
    Processes the candidate's audio answer: transcribes, evaluates, and prepares the next question.
    """
    if not audio_input:
        gr.Warning("Please record your answer before submitting.")
        # Return state and no-op UI updates
        return state, gr.update(), gr.update(), gr.update(), gr.update(interactive=True)

    # Disable the submit button to prevent multiple submissions
    yield state, gr.update(), gr.update(), gr.update(value="Processing..."), gr.update(interactive=False)

    # 1. Transcribe audio to text
    transcribed_answer = transcribe_audio(audio_input)
    if not transcribed_answer:
        transcribed_answer = "(Audio could not be transcribed)"

    # 2. Evaluate the answer
    current_question = state["questions"][state["current_question_index"]]['text']
    evaluation = evaluate_answer(current_question, transcribed_answer)

    # 3. Store the evaluation details in the state
    state["evaluations"].append({
        "question": current_question,
        "answer": transcribed_answer,
        **evaluation
    })

    # 4. Move to the next question
    state["current_question_index"] += 1

    # Check if the interview is over
    if state["current_question_index"] >= len(state["questions"]):
        # Interview is finished, show the results
        summary_data = get_interview_summary(state["evaluations"])
        final_score_text = f"Final Score: {summary_data['final_score']} / 10"
        summary_text = summary_data['summary']
        
        # Display results and hide the interview UI
        yield state, gr.update(visible=False), gr.update(visible=True), gr.update(value=final_score_text), gr.update(value=summary_text)
    else:
        # Ask the next question
        next_question_index = state["current_question_index"]
        next_question_text = state["questions"][next_question_index]['text']
        
        # Generate appreciation and transition
        ai_response = f"Thank you for your answer. Now for the next question."
        ai_response_audio = speak_text(ai_response)
        
        # Update UI with appreciation message
        yield state, gr.update(), gr.update(value="AI is responding..."), gr.update(value=ai_response_audio), gr.update(interactive=False)
        time.sleep(2) # Give user time to hear the transition
        
        # Generate audio for the next question
        question_audio_path = speak_text(next_question_text)
        
        # Update progress and question text
        progress_text = f"Question {next_question_index + 1} of {len(state['questions'])}"
        
        # Re-enable submit button and update UI for the next question
        yield state, gr.update(value=progress_text), gr.update(value=next_question_text), gr.update(value=question_audio_path), gr.update(interactive=True)

# --- Gradio UI Definition ---
with gr.Blocks(theme=gr.themes.Soft(), title="AI Interviewer") as demo:
    
    # State object to hold session data
    state = gr.State(value=initialize_state())
    
    gr.Markdown("# 🤖 AI Interviewer")
    gr.Markdown("Welcome! Please set up your interview, and the AI will guide you through the questions.")

    # --- 1. Setup Screen ---
    with gr.Row(visible=True) as setup_screen:
        with gr.Column():
            candidate_name_input = gr.Textbox(label="Your Name")
            role_input = gr.Textbox(label="Job Role You're Applying For")
            num_questions_slider = gr.Slider(minimum=3, maximum=10, value=5, step=1, label="Number of Questions")
            start_button = gr.Button("Start Interview", variant="primary")

    # --- 2. Interview Screen ---
    with gr.Row(visible=False) as interview_screen:
        with gr.Column(scale=2):
            progress_label = gr.Label(value="Question 1 of 5")
            webcam_feed = gr.Image(sources=["webcam"], label="Live Monitoring", streaming=True)
            question_audio = gr.Audio(autoplay=True, interactive=False, label="AI Interviewer")
            question_display = gr.Textbox(label="Current Question", interactive=False, lines=3)
        with gr.Column(scale=3):
            gr.Markdown("### Record Your Answer")
            audio_answer_input = gr.Audio(sources=["microphone"], type="filepath", label="Speak your answer here")
            submit_answer_button = gr.Button("Submit Answer", variant="primary")
            
    # --- 3. Results Screen ---
    with gr.Column(visible=False) as results_screen:
        gr.Markdown("## ✅ Interview Complete!")
        gr.Markdown("Thank you for completing the interview. Here is your summary.")
        final_score_display = gr.Label(label="Overall Performance")
        summary_display = gr.Textbox(label="Interview Summary", interactive=False, lines=8)


    # --- Event Handling Logic ---
    start_button.click(
        fn=start_interview,
        inputs=[candidate_name_input, role_input, num_questions_slider],
        outputs=[state, progress_label, setup_screen, interview_screen, question_display, question_audio]
    )

    submit_answer_button.click(
        fn=process_answer,
        inputs=[state, audio_answer_input],
        outputs=[state, interview_screen, results_screen, final_score_display, summary_display],
        concurrency_limit=1 # Prevent multiple clicks while processing
    ).then(
        fn=lambda: (gr.update(value=None), gr.update(interactive=True)), # Clear audio and re-enable button after processing
        outputs=[audio_answer_input, submit_answer_button]
    )


if __name__ == "__main__":
    demo.launch(debug=True)
