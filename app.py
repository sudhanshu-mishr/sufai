import os
import io
import json
import zipfile
import google.generativeai as genai
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def generate_code_from_api(prompt, api_key):
    # Prioritize user provided key, fallback to env variable
    effective_api_key = api_key if api_key else os.environ.get('GEMINI_API_KEY')

    if not effective_api_key:
        return {"error": "API Key is missing. Please configure GEMINI_API_KEY on the server or provide one in settings."}

    genai.configure(api_key=effective_api_key)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        system_instruction = """
        You are SUFAI, an elite AI Coding Agent.
        Your Mission: Generate high-quality, production-ready code based on user requests.

        Guidelines:
        1.  **Project Structure**: If the request implies a full project, generate a complete file structure.
        2.  **Code Quality**: Write clean, modern, and well-commented code. Follow best practices for the language.
        3.  **Completeness**: Ensure all necessary imports, configuration files (like requirements.txt, package.json), and instructions (README.md) are included.
        4.  **No Markdown Wrapper**: You must output PURE JSON. Do not wrap the JSON in markdown code blocks (```json ... ```).
        5.  **JSON Format**: The output must be a valid JSON object where keys are filenames (including paths if needed, e.g., "src/main.py") and values are the file contents strings.

        Persona:
        -   You are helpful, precise, and expert-level.
        -   You prefer modern frameworks and robust solutions.
        -   You do not explain your thought process outside the code comments or README.

        Example Output Format:
        {
            "main.py": "print('Hello World')",
            "README.md": "# Project\n\nRun with `python main.py`"
        }
        """

        full_prompt = f"{system_instruction}\n\nUser Request: \"{prompt}\""

        response = model.generate_content(full_prompt)
        text = response.text.strip()

        # Robust cleanup for markdown code blocks
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]

        if text.endswith('```'):
            text = text[:-3]

        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get('prompt')
    api_key = data.get('apiKey')

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    generated_files = generate_code_from_api(prompt, api_key)

    if "error" in generated_files:
        status_code = 500 if "API Key is missing" not in generated_files["error"] else 401
        return jsonify(generated_files), status_code

    return jsonify({"files": generated_files})

@app.route('/api/zip', methods=['POST'])
def create_zip():
    data = request.get_json()
    files = data.get('files')

    if not files:
        return jsonify({"error": "No files provided"}), 400

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename, content in files.items():
            zf.writestr(filename, content)

    memory_file.seek(0)

    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='sufai_generated_code.zip'
    )

if __name__ == '__main__':
    # Use PORT from environment for Render compatibility, default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
