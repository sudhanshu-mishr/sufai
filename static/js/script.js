document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const promptInput = document.getElementById('prompt');
    const apiKeyInput = document.getElementById('api-key');
    const resultSection = document.getElementById('result-section');
    const codePreview = document.getElementById('code-preview');
    const downloadBtn = document.getElementById('download-btn');
    const btnText = document.getElementById('btn-text');
    const loader = document.getElementById('loader');

    let currentFiles = null;

    generateBtn.addEventListener('click', async () => {
        const prompt = promptInput.value.trim();
        const apiKey = apiKeyInput.value.trim();

        if (!prompt) {
            alert('Please describe what you want to generate.');
            return;
        }

        if (!apiKey) {
            alert('Please enter your Gemini API Key.');
            return;
        }

        generateBtn.disabled = true;
        btnText.textContent = 'Generating...';
        loader.style.display = 'block';
        resultSection.classList.add('hidden');
        resultSection.classList.remove('visible');
        codePreview.innerHTML = '<p class="placeholder-text">Generating files...</p>';
        downloadBtn.disabled = true;

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt, apiKey })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to generate code');
            }

            const data = await response.json();
            currentFiles = data.files;

            // Render Preview
            codePreview.innerHTML = '';
            if (Object.keys(currentFiles).length === 0) {
                 codePreview.innerHTML = '<p class="placeholder-text">No code generated.</p>';
            } else {
                for (const [filename, content] of Object.entries(currentFiles)) {
                    const fileBlock = document.createElement('div');
                    fileBlock.className = 'file-block';

                    const header = document.createElement('div');
                    header.className = 'file-header';
                    header.textContent = filename;

                    const fileContent = document.createElement('pre');
                    fileContent.className = 'file-content';
                    const code = document.createElement('code');
                    code.textContent = content;
                    fileContent.appendChild(code);

                    fileBlock.appendChild(header);
                    fileBlock.appendChild(fileContent);
                    codePreview.appendChild(fileBlock);
                }
            }

            resultSection.classList.remove('hidden');
            // Trigger reflow
            void resultSection.offsetWidth;
            resultSection.classList.add('visible');
            downloadBtn.disabled = false;

        } catch (error) {
            alert(error.message);
        } finally {
            generateBtn.disabled = false;
            btnText.textContent = 'Generate Code';
            loader.style.display = 'none';
        }
    });

    downloadBtn.addEventListener('click', async () => {
        if (!currentFiles) return;

        downloadBtn.textContent = 'Preparing ZIP...';
        downloadBtn.disabled = true;

        try {
            const response = await fetch('/api/zip', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ files: currentFiles })
            });

            if (!response.ok) {
                throw new Error('Failed to create ZIP file');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'sufai_generated_code.zip';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

        } catch (error) {
            alert('Error downloading ZIP: ' + error.message);
        } finally {
            downloadBtn.textContent = 'Download ZIP';
            downloadBtn.disabled = false;
        }
    });
});
