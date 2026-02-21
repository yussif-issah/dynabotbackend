document.getElementById('uploadBtn').addEventListener('click', async () => {
  const files = document.getElementById('fileInput').files;
  const status = document.getElementById('uploadStatus');
  status.textContent = 'Uploading...';
  if (!files.length) {
    status.textContent = 'No files selected.';
    return;
  }
  const formData = new FormData();
  for (let i = 0; i < files.length; i++) formData.append('files', files[i]);
  try {
    const res = await fetch('/handle_uploaded_files/', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    status.textContent = data.message || JSON.stringify(data);
  } catch (e) {
    status.textContent = 'Upload failed: ' + e;
  }
});

document.getElementById('ingestBtn').addEventListener('click', async () => {
  const url = document.getElementById('urlInput').value;
  const status = document.getElementById('ingestStatus');
  if (!url) {
    status.textContent = 'Enter a URL first.';
    return;
  }
  status.textContent = 'Fetching...';
  try {
    const res = await fetch('/ingest_url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    const data = await res.json();
    status.textContent = data.message || JSON.stringify(data);
  } catch (e) {
    status.textContent = 'Ingest failed: ' + e;
  }
});

// Ingest plain text (written by user)
document.getElementById('textIngestBtn').addEventListener('click', async () => {
  const title = document.getElementById('textTitle').value;
  const text = document.getElementById('textInput').value;
  const status = document.getElementById('textStatus');
  if (!text || text.trim().length === 0) {
    status.textContent = 'Enter some text to ingest.';
    return;
  }
  status.textContent = 'Ingesting...';
  try {
    const res = await fetch('/ingest_text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, text })
    });
    const data = await res.json();
    status.textContent = data.message || JSON.stringify(data);
  } catch (e) {
    status.textContent = 'Ingest failed: ' + e;
  }
});

document.getElementById('testBtn').addEventListener('click', async () => {
  const status = document.getElementById('testStatus');
  try {
    const res = await fetch('/test');
    const data = await res.json();
    status.textContent = data.message || JSON.stringify(data);
  } catch (e) {
    status.textContent = 'Test failed: ' + e;
  }
});
