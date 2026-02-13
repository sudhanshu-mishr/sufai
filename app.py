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

def generate_code_from_gemini(prompt, api_key=None):
    # Always prioritize server key
    effective_api_key = os.environ.get('GEMINI_API_KEY')

    if not effective_api_key:
        return {"error": "Server Configuration Error: GEMINI_API_KEY is missing."}

    genai.configure(api_key=effective_api_key)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        system_instruction = """
        You are SUFAI, an elite AI Coding Agent specializing in web development.
        Your Mission: Generate complete, functional, and modern code for simple websites based on user requests.

        Guidelines:
        1.  **Output Format**: You must output PURE JSON. Keys are filenames, values are file contents.
        2.  **Single Page vs Multi-file**:
            - If the request is for a simple site, prefer a structure with `index.html`, `style.css`, and `script.js` (if needed).
            - If the request is very simple, you can combine CSS/JS into `index.html` but separate files are generally cleaner.
        3.  **Content Quality**:
            - Use modern CSS (Flexbox, Grid, Variables).
            - Use semantic HTML5.
            - Add comments explaining key sections.
            - Ensure the site is responsive.
        4.  **Completeness**: Include a `README.md` explaining how to open/run the site.

        Example Output Format:
        {
            "index.html": "<!DOCTYPE html><html>...</html>",
            "style.css": "body { background: #333; }",
            "README.md": "# My Site\n\nOpen index.html in your browser."
        }
        """

        full_prompt = f"{system_instruction}\n\nUser Request: \"{prompt}\""

        response = model.generate_content(full_prompt)
        text = response.text.strip()
        text = clean_json_text(text)

        return json.loads(text)
    except Exception as e:
        return {"error": f"Gemini Error: {str(e)}"}

def generate_code_from_huggingface(prompt, api_key=None):
    # Always prioritize server key
    effective_api_key = os.environ.get('HUGGINGFACE_API_KEY')

    if not effective_api_key:
         return {"error": "Server Configuration Error: HUGGINGFACE_API_KEY is missing."}

    try:
        repo_id = "meta-llama/Meta-Llama-3-8B-Instruct"
        client = InferenceClient(token=effective_api_key)

        system_instruction = """You are SUFAI, a web development AI.
Generate code for the user's request in valid JSON format only.
Keys: filenames. Values: file content.
Ensure HTML, CSS, and JS are valid and modern.
"""

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]

        response = client.chat_completion(
            messages=messages,
            model=repo_id,
            max_tokens=2000,
            temperature=0.2
        )

        text = response.choices[0].message.content.strip()

        # Hugging face models sometimes wrap in backticks too
        try:
            cleaned_text = clean_json_text(text)
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
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

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # Primary: Gemini
    generated_files = generate_code_from_gemini(prompt)

    # Fallback: Hugging Face if Gemini fails specifically due to configuration/key error
    if "error" in generated_files:
        error_msg = str(generated_files["error"])
        if "Server Configuration Error" in error_msg or "Gemini API Key is missing" in error_msg:
             print("Gemini unavailable, attempting fallback to Hugging Face...")
             hf_files = generate_code_from_huggingface(prompt)
             # If HF works, use it. If HF also errors, return the original Gemini error (or HF error)
             if "error" not in hf_files:
                 generated_files = hf_files
             else:
                 # If both fail, return concatenated error or just the Gemini one?
                 # Let's return the HF error as it was the last attempt
                 generated_files = hf_files

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
