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
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        full_prompt = f"""
        You are an AI coding agent named SUFAI.
        Your task is to generate code based on the user's request: "{prompt}"

        If the request implies a full project or multiple files, generate all necessary files.
        If it's a single script, generate that.

        IMPORTANT: You must format your response strictly as a JSON object where keys are filenames and values are the file contents.
        Do NOT include any markdown formatting (like ```json or ```), explanations, or text outside the JSON object.
        Just the raw JSON string.

        Example:
        {{
            "main.py": "print('Hello')",
            "requirements.txt": "flask"
        }}
        """

        response = model.generate_content(full_prompt)
        text = response.text.strip()

        # Clean up potential markdown code blocks if the model ignores the instruction
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
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

    if not prompt or not api_key:
        return jsonify({"error": "Prompt and API Key are required"}), 400

    generated_files = generate_code_from_api(prompt, api_key)

    if "error" in generated_files:
        return jsonify(generated_files), 500

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
    app.run(debug=True, port=5000)
