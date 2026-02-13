# SUFAI - AI Coding Agent

SUFAI is a web-based AI coding assistant that generates code based on your prompts using Google's Gemini models or Open Source models via Hugging Face. It allows you to preview the generated code and download it as a ZIP file.

## Features

-   **Dual AI Engines**:
    -   **Gemini (Google)**: High-quality code generation via `google-generativeai`.
    -   **Open Source GPT (Hugging Face)**: Uses models like Llama 3 via `huggingface_hub` Inference API.
-   **Configurable API Keys**: Use server-configured keys or provide your own in the settings.
-   **Code Preview**: View the generated file structure and content directly in the browser.
-   **Download as ZIP**: Download the entire generated project as a ZIP file.
-   **Modern UI**: Dark-themed, clean interface similar to modern coding tools.

## Setup

1.  **Clone the repository** (if applicable).
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the application**:
    ```bash
    python app.py
    ```
4.  **Open your browser**:
    Navigate to `http://127.0.0.1:5000`.

## Usage

1.  **Server-Side Keys (Recommended)**: Set the environment variables. The app will use these by default.
    ```bash
    export GEMINI_API_KEY="your_gemini_key"
    export HUGGINGFACE_API_KEY="your_hf_token"
    python app.py
    ```
2.  **User-Provided Key**: In the UI, expand "Configuration", select your model, and optionally enter a specific API key/token.
3.  Enter a prompt describing what you want to build.
4.  Click **Generate Code**.

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
    -   `GEMINI_API_KEY`
    -   `HUGGINGFACE_API_KEY` (Optional, but recommended for higher rate limits)
