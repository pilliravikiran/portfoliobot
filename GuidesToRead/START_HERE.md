# 🚀 START HERE — RaviBot in 10 minutes

> Welcome! This is the **first file you should open**.
> It walks you through every step in plain English.
> When you're done, you'll have a working AI chatbot on your own laptop.

---

## 📦 What you just got

```
llm_development/                  ← THE ONE folder you need
│
├── 📘 START_HERE.md              ← you are here
├── 📘 BUILD_GUIDE.docx           ← the full child-friendly teaching book
├── 📄 README.md                  ← short reference / table of contents
├── 📄 PORTFOLIO_INTEGRATION.md   ← how the chat bubble plugs into your Portfolio
│
├── ⚙️  requirements.txt           ← Python packages to install
├── 🔑 .env.example                ← copy → .env, paste your OpenAI key
├── 🚫 .gitignore                  ← files Git should ignore
│
├── 🧠 THE BRAIN (pure Python, all 4 files together)
│   ├── config.py                 ← all the knobs in one place
│   ├── prompts.py                ← the bot's personality
│   ├── ingest.py                 ← reads data/ → vector DB
│   └── chatbot.py                ← the smart router + RAG + general
│
├── 💬 THE 3 FACES (pick any one — they share the same brain)
│   ├── chat_app.py               ← Streamlit web app
│   ├── api.py                    ← FastAPI REST backend
│   └── widget/                   ← embeddable chat bubble
│       ├── widget.js
│       ├── widget.html           ← test page
│       └── README.md
│
├── 📚 data/                       ← the knowledge base (Ravi's resume)
│   ├── about.md
│   ├── skills.md
│   ├── experience.md
│   ├── projects.md
│   ├── education.md
│   ├── contact.md
│   └── faq.md
│
├── 🔧 build_guide.js              ← regenerates BUILD_GUIDE.docx
└── 📁 chroma_db/                  ← (auto-created when you run ingest.py)
```

---

## 🪜 The 7 steps (do them once, in order)

### Step 1 — Make sure Python is installed

Open a terminal (Command Prompt / PowerShell / Terminal) and type:

```bash
python --version
```

If you see `Python 3.10.something` or newer, you're good.
If not, install from <https://www.python.org/downloads/>.

---

### Step 2 — Move into this folder

```bash
cd C:\Users\MMS\Documents\Github\llm_development
```

(You only ever work from inside this folder.)

---

### Step 3 — Create a virtual environment

A "virtual environment" is a sandbox that keeps this project's packages
separate from everything else on your machine.

```bash
python -m venv venv
```

Now turn it on:

```bash
# Windows:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate
```

You'll know it worked because your prompt now starts with `(venv)`.

---

### Step 4 — Install all packages

```bash
pip install -r requirements.txt
```

(takes ~1 minute)

---

### Step 5 — Add your OpenAI key

Get a key from <https://platform.openai.com/api-keys>. Copy it (it starts
with `sk-`).

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` in Notepad / VS Code and paste your real key after `=`:

```
OPENAI_API_KEY=sk-paste-your-real-key-here
```

Save and close.

⚠️  Never share this file. `.gitignore` already prevents it from being
committed to GitHub.

---

### Step 6 — Build the knowledge base (ONE TIME)

```bash
python ingest.py
```

You should see something like:

```
Found 7 document(s) to index.
  reading about.md ...
  reading contact.md ...
  ...
Done. Indexed 28 chunks from 7 document(s).
```

This creates a `chroma_db/` folder. You only re-run this when you change
files inside `data/`.

---

### Step 7 — Start chatting! (pick any front-end)

You have three different "faces" for the same bot. Pick one:

#### 🅰️  Option A — Streamlit web app (easiest)

```bash
streamlit run chat_app.py
```

Your browser opens at `http://localhost:8501`. Try:
- "Who is Ravi?"
- "What's his strongest tech stack?"
- "Explain RAG in one paragraph."

#### 🅱️  Option B — FastAPI server + chat bubble on your Portfolio

```bash
uvicorn api:app --reload --port 8000
```

The API is now running at `http://localhost:8000`.
- Visit `http://localhost:8000/docs` to play with the auto-generated
  interactive API explorer.
- Open `C:\Users\MMS\Documents\Github\Portfolio\index.html` in a browser
  → you'll see a floating 💬 button in the bottom-right corner. Click it
  and chat!
- See `PORTFOLIO_INTEGRATION.md` for full details.

#### 🅲  Option C — Command line (for hackers)

```bash
python chatbot.py
```

Chat from the terminal. Type `quit` to exit.

---

## 🎯 What's special about this bot?

When you ask a question, RaviBot does something clever:

1. **A tiny LLM call decides** "is this about Ravi, or general?"
2. **If about Ravi** → it pulls the most relevant snippets from `data/`
   and answers using those facts (with source citations).
3. **If general** → it answers freely like ChatGPT does.

This is called **RAG** (Retrieval-Augmented Generation). It's the same
pattern most production AI chatbots use.

---

## 📖 Want to understand how every line works?

Open **`BUILD_GUIDE.docx`** — it's a 20-chapter friendly walk-through
covering:

- What an LLM is (with analogies)
- How embeddings work
- How chunking works
- A walkthrough of every Python file
- How to deploy it on the internet
- A glossary of every fancy word
- Ideas to extend the project

---

## 🆘 Troubleshooting

| Problem | Fix |
|---|---|
| `OPENAI_API_KEY is not set` | You forgot Step 5. Open `.env`, paste your key. |
| `No knowledge base found` | You forgot Step 6. Run `python ingest.py`. |
| Module not found | You skipped Step 3 or 4. Activate venv, then `pip install -r requirements.txt`. |
| Widget shows but won't chat | The FastAPI backend isn't running. Start `uvicorn api:app --port 8000` in another terminal. |
| `Port already in use` | Another app is using the port. Either close it or use `--port 8501` / `--port 8001`. |

---

## 💰 What will this cost me?

Using GPT-4o-mini + text-embedding-3-small:

- One-time indexing of all 7 docs ≈ **$0.0002**
- One full chat (router + answer) ≈ **$0.0006**
- → **~1,500 conversations cost about $1**.

You can also put a hard budget cap in your OpenAI account.

---

That's it. You're ready. Have fun! 🎉

— Ravi
