# 🔗 Portfolio Integration Guide

This document explains exactly how the chat bubble plugs into your
Portfolio site (`C:\Users\MMS\Documents\Github\Portfolio\`).

---

## 🏗️ How the two folders talk to each other

```
┌────────────────────────────┐         HTTP POST            ┌─────────────────────────────┐
│  Portfolio/                │ ─── /chat ─────────────────► │  llm_development/            │
│  ├── index.html            │                              │  └── api.py  (FastAPI)        │
│  └── ravibot-widget.js  ◄──┘                              │       │                        │
│         (the chat bubble)                                 │       └──► chatbot.py (brain)  │
└────────────────────────────┘ ◄── JSON answer + sources ── │              │                 │
                                                            │              └──► ChromaDB     │
                                                            └─────────────────────────────┘
```

- **Frontend (Portfolio):** a small JavaScript file (`ravibot-widget.js`)
  injects a chat bubble into every page of the portfolio. When you type
  a question and press Send, it POSTs JSON to the backend.
- **Backend (llm_development):** a FastAPI server reads the question,
  runs the smart router + RAG pipeline, and returns the answer as JSON.

You can deploy them **independently** later (Portfolio on GitHub Pages /
Netlify / Vercel, API on Render / Railway / Azure).

---

## ✅ What's already wired up

I've already done these two things for you:

1. **`Portfolio/ravibot-widget.js`** — the chat-bubble script lives next
   to your `index.html`.
2. **`Portfolio/index.html`** — has this line just before `</body>`:

   ```html
   <script src="ravibot-widget.js" defer></script>
   ```

So when you open `index.html`, the bubble appears automatically.

---

## 🏃 To see it work locally (90 seconds)

### Terminal 1 — start the AI backend

```bash
cd C:\Users\MMS\Documents\Github\llm_development
venv\Scripts\activate
uvicorn api:app --reload --port 8000
```

You should see:

```
Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Leave this terminal running.

### Terminal 2 — open the Portfolio

Pick one:

- **Quick way:** double-click
  `C:\Users\MMS\Documents\Github\Portfolio\index.html` to open it in
  your browser.
- **Proper way (a tiny local web server):**
  ```bash
  cd C:\Users\MMS\Documents\Github\Portfolio
  python -m http.server 5500
  ```
  Then visit `http://localhost:5500/` in your browser.

You'll see:
- The portfolio page loads as normal.
- A purple/blue **💬 bubble** in the bottom-right corner with a gentle
  pulse animation.
- Click it → a chat panel slides up.
- A welcome message + 4 suggestion chips appear.
- Try clicking "Who is Ravi?" — it should answer in 1-2 seconds with
  source filenames at the bottom of the reply.

---

## 🎨 Customising the widget

Open `Portfolio/ravibot-widget.js` and edit the `CONFIG` block near
the top:

```js
const CONFIG = {
  API_URL:  "http://localhost:8000/chat",                  // ← change after deploy
  BOT_NAME: "RaviBot",                                     // ← rename the bot
  GREETING: "Hi 👋 I'm RaviBot — ask me anything...",      // ← first message
  PRIMARY:  "linear-gradient(135deg,#0071e3,#5856d6)",     // ← bubble + button colour
  POSITION: { right: "24px", bottom: "24px" },             // ← corner placement
};
```

To change the suggestion chips, edit the `SUGGESTIONS` array a bit
further down in the same file.

---

## 🌍 Deploying to the public internet

### Step 1 — Deploy the backend

Pick one of these (all have free tiers):

- **Render** — easiest. Connect GitHub repo, set start command:
  `uvicorn api:app --host 0.0.0.0 --port $PORT`
- **Railway** — same pattern.
- **Azure App Service / Fly.io** — also fine.

Set environment variable in the dashboard:

```
OPENAI_API_KEY = sk-...
```

After deploy, you'll get a URL like
`https://ravibot-api.onrender.com`.

### Step 2 — Point the widget at the deployed URL

In `Portfolio/ravibot-widget.js`, change:

```js
API_URL: "http://localhost:8000/chat",
```

to:

```js
API_URL: "https://ravibot-api.onrender.com/chat",
```

### Step 3 — Tighten CORS

In `llm_development/api.py`, change:

```python
allow_origins=["*"],
```

to:

```python
allow_origins=["https://ravikiranpilli.com", "https://www.ravikiranpilli.com"],
```

This way only your portfolio can talk to your API.

### Step 4 — Deploy the Portfolio

`Portfolio/` is a static folder. Drop it on Netlify, Vercel, GitHub
Pages, or Cloudflare Pages — all free.

Done. Your chat bubble is now live on the internet. 🎉

---

## 🔄 Keeping the two `widget.js` files in sync

There are two copies of the widget script:

| File | Purpose |
|---|---|
| `llm_development/widget/widget.js` | Master / development copy |
| `Portfolio/ravibot-widget.js` | The one your site actually uses |

If you edit one, copy it to the other so they don't drift. The simplest
recipe (Windows):

```bash
copy llm_development\widget\widget.js Portfolio\ravibot-widget.js
```

---

## ❓ FAQ

**Q: Can I put the widget on websites other than my Portfolio?**
Yes — just add `<script src="path/to/ravibot-widget.js" defer></script>`
to any HTML page. As long as your API allows that origin in CORS, the
chat works.

**Q: Does it remember conversations across page reloads?**
No, history lives in memory and resets when you close the tab. To
persist, add `localStorage.setItem(...)` after each exchange and load it
back on page open.

**Q: Will the widget slow down my portfolio?**
No. The widget script is ~10KB, loaded with `defer` so it doesn't block
rendering. The chat panel only builds when the user opens it.

**Q: What happens if my API is down?**
The bubble still shows. If the user opens it and sends a message, they
get a friendly error: *"Sorry — I couldn't reach the server."*
