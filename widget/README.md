# 💬 The chat widget

This subfolder holds the **embeddable chat bubble** — a single-file
JavaScript widget that injects a floating chat button onto any HTML page
and talks to the FastAPI backend in `../api.py`.

## Files

| File | Purpose |
|---|---|
| `widget.js` | The widget itself — pure JS, no dependencies, ~10 KB |
| `widget.html` | A standalone demo page that loads `widget.js` |
| `README.md` | This file |

> **Note:** The version of `widget.js` your Portfolio actually uses lives
> at `..\..\Portfolio\ravibot-widget.js` (next to `index.html`). The two
> files should stay identical — see `PORTFOLIO_INTEGRATION.md` § *Keeping
> the two widget.js files in sync* for the easy `copy` command.

---

## Try it locally

### 1. Start the FastAPI backend

```bash
cd ..              # back to llm_development/
venv\Scripts\activate
uvicorn api:app --reload --port 8000
```

### 2. Open the demo page

Either double-click `widget.html`, or serve the folder:

```bash
python -m http.server 5500
```

Then visit `http://localhost:5500/widget/widget.html`. Click the
floating 💬 button in the bottom-right corner.

---

## Embed it elsewhere

On any HTML page, just before `</body>`:

```html
<script src="path/to/widget.js" defer></script>
```

Change the `CONFIG` block at the top of `widget.js`:

```js
const CONFIG = {
  API_URL:  "https://your-deployed-api.com/chat",
  BOT_NAME: "RaviBot",
  GREETING: "Hi! I'm RaviBot — ask me anything.",
  PRIMARY:  "linear-gradient(135deg,#0071e3,#5856d6)",
  POSITION: { right: "24px", bottom: "24px" },
};
```

That's the only file you ever touch.

---

For full deployment instructions see `..\PORTFOLIO_INTEGRATION.md`.
