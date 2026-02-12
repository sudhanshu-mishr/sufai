# SUFAI - AI Coding Agent

SUFAI is a web-based AI coding assistant that generates code based on your prompts using Google's Gemini models. It allows you to preview the generated code and download it as a ZIP file.

## Features

-   **AI Code Generation**: Uses Google Gemini (via `google-generativeai`) to generate code for scripts, full projects, or websites.
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

1.  Enter your **Gemini API Key**. You can get a free one from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Enter a prompt describing what you want to build (e.g., "A simple Flask app with a login page").
3.  Click **Generate Code**.
4.  Review the generated files in the preview area.
5.  Click **Download ZIP** to get the files.

## Dependencies

-   Flask
-   google-generativeai
