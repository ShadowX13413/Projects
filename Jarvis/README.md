# J.A.R.V.I.S. — Local UI and Python agent

Quick guide to run the local UI and reduce system lag.

Prerequisites
- Python 3.9+
- Install dependencies:

```bash
pip install -r requirements.txt
```

Run modes
- CLI interactive (original):

```bash
python jarvis.py
```

- Run local web UI (serves `jarvis.html` and provides `/api/chat`):

```bash
python jarvis.py --serve
```

Notes about lag reduction
- The Python process attempts to lower its OS priority (via `psutil`) so heavy model inference impacts the system less.
- If you still see lag, run Jarvis with `--serve` and minimize other CPU-heavy apps, or install a smaller model for `ollama`.

Performance tuning
- Use a smaller local model to reduce CPU/GPU usage. Start the server with `--model` to pick a lighter model, for example:

```bash
python jarvis.py --serve --model smaller-model-name
```

- Limit response size with `--max-tokens`:

```bash
python jarvis.py --serve --max-tokens 256
```

- Disable server-side TTS (use browser TTS in the UI) to avoid additional CPU overhead:

```bash
python jarvis.py --serve --no-tts
```

- If the server is still heavy, prefer running the UI with `--no-tts` and let the browser speak replies (toggle "Browser TTS" in the UI).
 
Fast mode (single-turn, minimal)
- To get the fastest possible offline replies, run the server in fast mode. This sends only a single user message per request, disables tools, and avoids the extra function/resolution call which saves a lot of time:

```bash
python jarvis.py --serve --fast --model <smaller-model-name> --max-tokens 256 --no-tts
```

Use a smaller local model (check your Ollama models) to make replies quicker.

Browser-only fallback
- Open `jarvis.html` in the browser for a simple local UI. For full model replies, run `python jarvis.py --serve` and use the page served by that process.
