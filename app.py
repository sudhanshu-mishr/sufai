import os
import io
import json
import zipfile
import requests
import google.generativeai as genai
from huggingface_hub import InferenceClient
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def clean_json_text(text):
    text = text.strip()
    # Robust cleanup for markdown code blocks
    if text.startswith('```json'):
        text = text[7:]
    elif text.startswith('```'):
        text = text[3:]

    if text.endswith('```'):
        text = text[:-3]
    return text.strip()

def generate_code_from_gemini(prompt, api_key):
    effective_api_key = api_key if api_key else os.environ.get('GEMINI_API_KEY')

    if not effective_api_key:
        return {"error": "Gemini API Key is missing. Please configure GEMINI_API_KEY on the server or provide one in settings."}

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

        Example Output Format:
        {
            "main.py": "print('Hello World')",
            "README.md": "# Project\n\nRun with `python main.py`"
        }
        """

        full_prompt = f"{system_instruction}\n\nUser Request: \"{prompt}\""

        response = model.generate_content(full_prompt)
        text = response.text.strip()
        text = clean_json_text(text)

        return json.loads(text)
    except Exception as e:
        return {"error": f"Gemini Error: {str(e)}"}

def generate_code_from_huggingface(prompt, api_key):
    effective_api_key = api_key if api_key else os.environ.get('HUGGINGFACE_API_KEY')

    # Check if we have a key, if not we might still try if the model allows free anonymous access (rare for inference API),
    # but usually requires a token.
    if not effective_api_key:
        return {"error": "Hugging Face Token is missing. Please configure HUGGINGFACE_API_KEY on the server or provide one in settings."}

    try:
        # Using Meta-Llama-3-8B-Instruct which is often available
        repo_id = "meta-llama/Meta-Llama-3-8B-Instruct"

        client = InferenceClient(token=effective_api_key)

        system_instruction = """You are SUFAI, an elite AI Coding Agent.
Your task is to generate code based on the user's request.
IMPORTANT: You must format your response strictly as a JSON object where keys are filenames and values are the file contents.
Do NOT include any markdown formatting, explanations, or text outside the JSON object.
Example: {"main.py": "print('Hello')"}
"""

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]

        # InferenceClient.chat_completion is correct for newer hugginface_hub versions
        # Ensure we pass the model name if initialized without one, or just rely on default if client init with token only?
        # InferenceClient(token=...) defaults to a generic endpoint, usually we need to specify model in call or init.
        # Let's specify it in the call.

        response = client.chat_completion(
            messages=messages,
            model=repo_id,
            max_tokens=2000,
            temperature=0.2
        )

        text = response.choices[0].message.content.strip()

        # Attempt to clean up JSON
        try:
            cleaned_text = clean_json_text(text)
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            # Fallback if the model returned extra text despite instructions
            # Sometimes models return "Here is the JSON:\n{...}"
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
            else:
                raise ValueError("Could not parse JSON from model response")

    except Exception as e:
        return {"error": f"Hugging Face Error: {str(e)}"}

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get('prompt')
    api_key = data.get('apiKey')
    model_type = data.get('model', 'gemini') # Default to gemini

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    if model_type == 'huggingface':
        generated_files = generate_code_from_huggingface(prompt, api_key)
    else:
        generated_files = generate_code_from_gemini(prompt, api_key)

    if isinstance(generated_files, dict) and "error" in generated_files:
        status_code = 500
        if "API Key is missing" in generated_files["error"] or "Token is missing" in generated_files["error"]:
            status_code = 401
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
