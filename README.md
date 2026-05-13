# 🤖 PortfolioBot — API + Portfolio widget

A minimal AI chatbot setup: **FastAPI backend** + **embeddable JS widget**
on your portfolio. Built on OpenAI GPT-4o-mini + ChromaDB + RAG.

---

## 📁 What's in this folder

```
llm_development/
├── .env                ← your OpenAI key (gitignored)
├── .env.example        ← template (safe to commit)
├── .gitignore
│
├── config.py           ← settings (model names, chunk sizes)
├── prompts.py          ← the 3 system prompts
├── ingest.py           ← reads data/ → builds chroma_db/
├── chatbot.py          ← the brain (RaviBot class)
├── api.py              ← THE FASTAPI SERVER  ◄── main entry point
│
├── requirements.txt    ← Python packages
├── runtime.txt         ← Python version for Render
├── start.sh            ← startup script for Render
│
├── data/               ← knowledge base (markdown files)
│   ├── about.md
│   ├── contact.md
│   ├── education.md
│   ├── experience.md
│   ├── faq.md
│   ├── projects.md
│   └── skills.md
│
└── chroma_db/          ← vector database (auto-built by ingest.py)
```

And in your **Portfolio** folder (separate repo):
- `Portfolio/index.html` — has `<script src="ravibot-widget.js" defer></script>` near `</body>`
- `Portfolio/ravibot-widget.js` — the floating chat bubble

---

## 🏃 Running locally

```powershell
cd C:\Users\MMS\Documents\Github\llm_development

# one-time setup
python -m venv pbot
pbot\Scripts\activate
pip install -r requirements.txt
copy .env.example .env          # then paste your OpenAI key in .env
python ingest.py                # builds chroma_db/

# start the API
uvicorn api:app --reload --port 8000
```

API is now live at **http://localhost:8000**.
Visit **http://localhost:8000/docs** for the interactive playground.

In a **separate** terminal, serve the portfolio:

```powershell
cd C:\Users\MMS\Documents\Github\Portfolio
python -m http.server 5500
```

Open **http://localhost:5500/** in your browser → click the 💬 bubble → chat.

---

## 🌐 How it all connects

```
┌──────────────────────────────┐        ┌──────────────────────────────┐
│ Portfolio (HTML+JS)           │        │ FastAPI server (api.py)        │
│ at http://localhost:5500/     │ ─POST─►│ at http://localhost:8000        │
│                               │        │                                │
│ ravibot-widget.js does:       │  /chat │ Receives JSON {question}        │
│   fetch(API_URL, {            │        │ Calls chatbot.RaviBot.ask()     │
│     question: "Who is Ravi?"  │ ◄─JSON─│ Returns JSON {answer, sources} │
│   })                          │ answer │                                │
└──────────────────────────────┘        └──────────────────────────────┘
                                                       │
                                                       ▼
                                          chatbot.py uses:
                                          - prompts.py (system prompts)
                                          - chroma_db/ (vector search)
                                          - OpenAI API (LLM)
```

---

## 🚀 Deploying

See `DEPLOYMENT.md` for the full recipe:
- Portfolio → Vercel (or Cloudflare Pages)
- FastAPI backend → Render (free tier)
- Wire them together with CORS + production API URL

---

Built by Ravi Kiran Pilli · mail2pilliravikiran@gmail.com
