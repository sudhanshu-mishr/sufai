# SUFAI - AI Coding Agent

SUFAI is a web-based AI coding assistant that generates code based on your prompts using Google's Gemini models. It allows you to preview the generated code and download it as a ZIP file.

## Features

-   **AI Code Generation**: Uses Google Gemini (via `google-generativeai`) to generate code for scripts, full projects, or websites.
-   **Configurable API Key**: Use a server-configured key or provide your own in the settings.
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

1.  **Server-Side Key (Recommended)**: Set the `GEMINI_API_KEY` environment variable. The app will use this by default, so users don't need to enter one.
    ```bash
    export GEMINI_API_KEY="your_api_key_here"
    python app.py
    ```
2.  **User-Provided Key**: If no server key is set, or if you want to override it, expand the "Configuration" section in the UI and enter your Gemini API Key.
3.  Enter a prompt describing what you want to build.
4.  Click **Generate Code**.

## Dependencies

-   Flask
-   google-generativeai
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
4.  **Important**: In the Render Dashboard, go to the **Environment** tab and add an Environment Variable named `GEMINI_API_KEY` with your Gemini API Key.
