# SUFAI - AI Coding Agent

SUFAI is a specialized AI Coding Agent designed to generate complete, simple websites and code snippets. It simplifies the development process by handling the entire code generation flow server-side, providing users with a ready-to-download ZIP file.

## Features

-   **One-Click Code Generation**: Simply enter a prompt, and SUFAI generates the code. No configuration needed.
-   **Dual AI Engine**:
    -   **Primary**: Google Gemini (via `google-generativeai`).
    -   **Fallback**: Open Source GPT (Llama 3 via Hugging Face) if Gemini is unavailable.
-   **Web Development Specialist**: "Trained" via system prompting to produce modern HTML5, CSS3, and JavaScript structures.
-   **Code Preview**: View generated files directly in the browser.
-   **ZIP Download**: Get the entire project structure in a single ZIP file.
-   **Modern UI**: Clean, dark-themed interface focused on the task.

## Setup

1.  **Clone the repository** (if applicable).
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the application**:
    ```bash
    export GEMINI_API_KEY="your_gemini_key"
    export HUGGINGFACE_API_KEY="your_hf_token" # Optional, for fallback
    python app.py
    ```
4.  **Open your browser**:
    Navigate to `http://127.0.0.1:5000`.

## Dependencies

-   Flask
-   google-generativeai
-   huggingface_hub
-   gunicorn

# Deployment on Render

This project is configured for deployment on [Render](https://render.com).

## Automatic Deployment

1.  Create a new Web Service on Render.
2.  Connect your GitHub repository.
3.  Render will automatically detect the configuration from `render.yaml`.
    -   **Runtime**: Python
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `gunicorn app:app`
4.  **Important**: In the Render Dashboard, go to the **Environment** tab and add:
    -   `GEMINI_API_KEY` (Required)
    -   `HUGGINGFACE_API_KEY` (Optional, for fallback capability)
