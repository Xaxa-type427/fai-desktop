# FAI Desktop P0 setup

This is a **source prototype**, not a packaged Windows application. Requires Python 3.9+ with Tkinter on Windows.

Set the following environment variables in Windows PowerShell (replace placeholders with values from your actual VPS deployment):

```powershell
$env:FAI_VPS_BASE_URL = 'https://YOUR-SECURE-VPS-ENDPOINT/v1'
$env:FAI_VPS_MODEL = 'YOUR-AVAILABLE-MODEL-ID'
$env:FAI_VPS_API_KEY = 'YOUR-API-KEY'
python fai_desktop.py
```

The endpoint must provide OpenAI-compatible `POST /chat/completions` and valid TLS. Do not put keys in GitHub or expose an unauthenticated inference endpoint publicly. The app does not yet control your PC, capture the screen, or use voice; those are future permission-gated features.

## Verification gate

1. Confirm VPS inference service is actually running and the configured model is returned by `/models`.
2. Send one harmless test message through the desktop UI and verify a valid response.
3. Only after chat passes, implement the authorized GitHub Bridge → SQLite write/readback test and collect evidence.

Status: source committed; live VPS round-trip **not tested**.
