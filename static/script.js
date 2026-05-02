const textInput = document.getElementById('text-input');
const btnFixTags = document.getElementById('btn-fix-tags');
const btnSave = document.getElementById('btn-save');
const btnGenerate = document.getElementById('btn-generate');
const consoleOutput = document.getElementById('console-output');
const btnClearConsole = document.getElementById('btn-clear-console');
const audioPlayerContainer = document.getElementById('audio-player-container');
const audioPlayer = document.getElementById('audio-player');
const downloadLink = document.getElementById('download-link');

function log(message, type = 'info') {
    const line = document.createElement('div');
    line.className = `log-line ${type}`;
    const timestamp = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    // Stringify if it's an object (for better error visibility)
    let displayMessage = message;
    if (typeof message === 'object' && message !== null) {
        displayMessage = JSON.stringify(message, null, 2);
    }
    
    line.innerText = `[${timestamp}] ${displayMessage}`;
    consoleOutput.appendChild(line);
    consoleOutput.scrollTop = consoleOutput.scrollHeight;
}

btnClearConsole.addEventListener('click', () => {
    consoleOutput.innerHTML = '';
});

btnFixTags.addEventListener('click', async () => {
    const text = textInput.value;
    if (!text) return log('Please enter some text first.', 'error');

    try {
        btnFixTags.disabled = true;
        log('Sending request to Groq to fix tags...');
        
        const response = await fetch('/api/fix-tags', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fix tags');
        }

        const data = await response.json();
        textInput.value = data.fixed_text;
        log('Tags optimized successfully by AI.');
    } catch (err) {
        log(`Error: ${err.message}`, 'error');
    } finally {
        btnFixTags.disabled = false;
    }
});

btnSave.addEventListener('click', async () => {
    const text = textInput.value;
    if (!text) return log('Nothing to save.', 'error');

    try {
        btnSave.disabled = true;
        log('Saving script to server...');
        
        const response = await fetch('/api/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        if (!response.ok) throw new Error('Failed to save script');

        const data = await response.json();
        log(`Script saved as ${data.filename} in 'saved_scripts' folder.`);
        
        // Also trigger local browser download
        const blob = new Blob([text], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = data.filename;
        a.click();
        window.URL.revokeObjectURL(url);
        
    } catch (err) {
        log(`Error: ${err.message}`, 'error');
    } finally {
        btnSave.disabled = false;
    }
});

const refVoiceUpload = document.getElementById('ref-voice-upload');
const uploadStatus = document.getElementById('upload-status');

let currentRefVoice = null;

refVoiceUpload.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
        log(`Uploading reference voice: ${file.name}...`);
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Upload failed');

        const data = await response.json();
        currentRefVoice = data.filename;
        uploadStatus.innerText = `Using: ${file.name}`;
        log(`Voice profile '${file.name}' ready for cloning.`);
    } catch (err) {
        log(`Upload Error: ${err.message}`, 'error');
        uploadStatus.innerText = 'Upload failed';
    }
});

btnGenerate.addEventListener('click', async () => {
    const text = textInput.value;
    if (!text) return log('Please enter some text first.', 'error');

    try {
        btnGenerate.disabled = true;
        btnGenerate.innerHTML = '<span class="icon">⌛</span> Generating...';
        log('Initializing audio generation (this may take a moment on CPU)...');
        
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                text,
                audio_prompt: currentRefVoice 
            })
        });

        if (!response.ok) {
            let errorMessage = 'Generation failed';
            try {
                const errorData = await response.json();
                errorMessage = typeof errorData.detail === 'object' ? JSON.stringify(errorData.detail) : (errorData.detail || errorMessage);
            } catch (e) {
                errorMessage = `Server Error: ${response.status} ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }

        const data = await response.json();
        log('Audio generated successfully.');
        
        audioPlayer.src = data.audio_url;
        downloadLink.href = data.audio_url;
        audioPlayerContainer.classList.remove('hidden');
        audioPlayer.play();
        
    } catch (err) {
        log(`Error: ${err.message}`, 'error');
    } finally {
        btnGenerate.disabled = false;
        btnGenerate.innerHTML = '<span class="icon">⚡</span> Generate Audio';
    }
});
