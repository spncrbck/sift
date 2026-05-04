const tabs = document.querySelectorAll('.tab');
const panels = document.querySelectorAll('.tab-panel');
const form = document.getElementById('recipe-form');
const submitBtn = document.getElementById('submit-btn');
const resultEl = document.getElementById('result');
const downloadLink = document.getElementById('download-link');
const previewLink = document.getElementById('preview-link');
const errorEl = document.getElementById('error');
const errorMsg = document.getElementById('error-msg');
const loadingEl = document.getElementById('loading');

let activeTab = 'text';

tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    tabs.forEach(t => t.classList.remove('active'));
    panels.forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    activeTab = tab.dataset.tab;
    document.getElementById(`panel-${activeTab}`).classList.add('active');
  });
});

// File input label updates
['image', 'pdf'].forEach(type => {
  const input = document.getElementById(`${type}-input`);
  const filename = document.getElementById(`${type}-filename`);
  input.addEventListener('change', () => {
    filename.textContent = input.files[0]?.name || '';
  });
});

// Drag and drop
document.querySelectorAll('.upload-area').forEach(area => {
  area.addEventListener('dragover', e => {
    e.preventDefault();
    area.classList.add('drag-over');
  });
  area.addEventListener('dragleave', () => area.classList.remove('drag-over'));
  area.addEventListener('drop', e => {
    e.preventDefault();
    area.classList.remove('drag-over');
    const input = area.querySelector('input[type="file"]');
    if (e.dataTransfer.files.length) {
      input.files = e.dataTransfer.files;
      input.dispatchEvent(new Event('change'));
    }
  });
});

form.addEventListener('submit', async e => {
  e.preventDefault();
  setLoading(true);

  const formData = new FormData();

  if (activeTab === 'text') {
    const text = form.querySelector('textarea[name="text"]').value.trim();
    if (!text) { showError('Please paste a recipe first.'); setLoading(false); return; }
    formData.append('text', text);
  } else if (activeTab === 'image') {
    const file = document.getElementById('image-input').files[0];
    if (!file) { showError('Please select an image.'); setLoading(false); return; }
    formData.append('image', file);
  } else {
    const file = document.getElementById('pdf-input').files[0];
    if (!file) { showError('Please select a PDF.'); setLoading(false); return; }
    formData.append('pdf', file);
  }

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 120000); // 2 minute timeout
    const res = await fetch('/convert', { method: 'POST', body: formData, signal: controller.signal });
    clearTimeout(timeout);
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      showError(data.detail || `Error ${res.status}`);
      return;
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const disposition = res.headers.get('content-disposition') || '';
    const match = disposition.match(/filename="(.+?)"/);
    const filename = match ? match[1] : 'recipe.html';
    downloadLink.href = url;
    downloadLink.download = filename;
    previewLink.href = url;
    showResult();
  } catch (err) {
    if (err.name === 'AbortError') {
      showError('Request timed out after 2 minutes. The server might be slow or OCR is taking too long.');
    } else {
      showError('Something went wrong. Please try again.');
    }
  } finally {
    setLoading(false);
  }
});

function setLoading(on) {
  submitBtn.disabled = on;
  loadingEl.classList.toggle('hidden', !on);
  if (on) { resultEl.classList.add('hidden'); errorEl.classList.add('hidden'); }
}

function showResult() {
  resultEl.classList.remove('hidden');
  errorEl.classList.add('hidden');
}

function showError(msg) {
  errorMsg.textContent = msg;
  errorEl.classList.remove('hidden');
  resultEl.classList.add('hidden');
}
