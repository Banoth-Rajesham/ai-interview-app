# 🤖 AI Interviewer Project

This is a complete, production-ready AI Interview Project built with Python and Gradio. The application conducts a simulated job interview where an AI asks questions via voice, listens to the candidate's spoken responses, transcribes them, and provides an evaluation and summary at the end.

## ✨ Features

- **Dynamic Question Generation**: Uses OpenAI's GPT models to generate relevant interview questions based on the specified job role.
- **Voice-based Interaction**: The AI asks questions using Text-to-Speech (TTS), and the candidate answers by speaking into their microphone.
- **Live Transcription**: Candidate's spoken answers are transcribed in real-time using OpenAI's Whisper API.
- **AI-Powered Evaluation**: Each answer is evaluated by an LLM, which provides a score (0-10) and constructive feedback.
- **Live Webcam Monitoring**: The candidate's webcam is active during the interview for proctoring simulation.
- **Final Summary**: At the end of the interview, a comprehensive summary and an average score are provided.
- **Modular & Extensible**: The codebase is organized into modules for LLM, STT, and TTS utilities, making it easy to extend or swap components.
- **Deployable**: Ready to be deployed as a Gradio App on Hugging Face Spaces.

## 📂 Project Structure

```
.
├── app.py              # Main Gradio application entrypoint
├── llm_utils.py        # Utilities for OpenAI LLM interaction (questions, evaluation)
├── stt_utils.py        # Utilities for Speech-to-Text (Whisper API)
├── tts_utils.py        # Utilities for Text-to-Speech (gTTS)
├── questions.json      # Fallback static question bank
├── requirements.txt    # Python dependencies
├── .gitignore          # Files to be ignored by Git
└── README.md           # This file
```

## ⚙️ Setup and Installation (Local)

Follow these steps to set up and run the project on your local machine.

### 1. Prerequisites

- **Python 3.8+**
- **FFmpeg**: This is a critical dependency required by the `pydub` library to process audio files.
  - **On macOS (using Homebrew):**
    ```bash
    brew install ffmpeg
    ```
  - **On Ubuntu/Debian:**
    ```bash
    sudo apt update && sudo apt install ffmpeg
    ```
  - **On Windows:**
    Download the binaries from the [official FFmpeg website](https://ffmpeg.org/download.html), extract them, and add the `bin` directory to your system's PATH environment variable.

### 2. Clone the Repository

```bash
git clone <repository_url>
cd ai-interviewer-project
```

### 3. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 4. Install Dependencies

Install all the required Python packages from `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

You need an OpenAI API key to use the LLM and Whisper models.

1.  Create a file named `.env` in the root directory of the project.
2.  Add your OpenAI API key to this file:

    ```
    OPENAI_API_KEY="sk-YourSecretOpenAIKeyGoesHere"
    # Optional: Specify a different model
    # OPENAI_MODEL="gpt-4"
    ```

## 🚀 Running the Application

Once the setup is complete, you can run the Gradio application with a single command:

```bash
python app.py
```

This will start a local web server. Open the URL provided in the terminal (usually `http://127.0.0.1:7860`) in your web browser to start the interview.

## 🌐 Deployment to Hugging Face Spaces

This application is designed to be easily deployed on Hugging Face Spaces.

1.  **Create a Hugging Face Account**: If you don't have one, sign up at [huggingface.co](https://huggingface.co/).

2.  **Create a New Space**:
    - Click on your profile picture and select "New Space".
    - Give your Space a name (e.g., `ai-interviewer`).
    - Select "**Gradio**" as the Space SDK.
    - Choose a hardware configuration (the free CPU tier is sufficient to start).
    - Click "Create Space".

3.  **Upload Project Files**:
    - You can upload your files directly via the web interface or by cloning the repository created for your Space and pushing your code via Git.
    - Make sure you upload all the files: `app.py`, `llm_utils.py`, `stt_utils.py`, `tts_utils.py`, `questions.json`, and `requirements.txt`.

4.  **Add Your API Key as a Secret**:
    - **Do not** upload your `.env` file or hardcode your API key.
    - In your Hugging Face Space, go to the "**Settings**" tab.
    - Scroll down to "**Repository secrets**".
    - Click "**New secret**".
    - For the **Name**, enter `OPENAI_API_KEY`.
    - For the **Value**, paste your actual OpenAI API key (`sk-...`).
    - Click "Save secret".

The Space will automatically detect your `requirements.txt` file, install the dependencies, and run `app.py`. Your AI Interviewer will now be live and accessible to anyone with the link!
