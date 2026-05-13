# 📓 Learn RaviBot in Google Colab — line-by-line

> Open the notebook **`colab/RaviBot_Learn_In_Colab.ipynb`** in Google
> Colab and run cells one by one. You'll see exactly what each file does
> and what the data looks like at every stage.

---

## ❓ Which files do I need to run, and in what order?

Your project has **9 Python / config files**. Only **3 of them are
"runnable"** — the rest are imported as libraries or read as config.

### The file-execution map

```
                ┌────────────────────────────────────────────┐
                │            FILES YOU NEVER RUN              │
                │  (they get loaded by other files)           │
                ├────────────────────────────────────────────┤
                │  config.py        ← knobs / paths           │
                │  prompts.py       ← the 3 system prompts    │
                │  requirements.txt ← list of pip packages    │
                │  .env             ← your OpenAI key         │
                │  data/*.md        ← your knowledge base     │
                └────────────────────────────────────────────┘
                                    │
                                    │ imported by
                                    ▼
                ┌────────────────────────────────────────────┐
                │       THE 3 FILES YOU ACTUALLY RUN          │
                ├────────────────────────────────────────────┤
                │                                              │
                │  1. python ingest.py                         │
                │     → reads data/ → creates chroma_db/       │
                │     → RUN ONCE (and again if data/ changes)  │
                │                                              │
                │  2. python chatbot.py                        │
                │     → command-line chat (for testing)        │
                │     → RUN whenever you want to chat in CLI   │
                │                                              │
                │  3. Pick a UI:                               │
                │     • streamlit run chat_app.py              │
                │     • uvicorn api:app --port 8000            │
                │     → RUN to start the server                │
                │                                              │
                └────────────────────────────────────────────┘
```

### TL;DR — the flow

```
   STEP 1               STEP 2                STEP 3
┌──────────┐         ┌──────────┐          ┌──────────┐
│ ingest.py│ ──────► │chatbot.py│ ───────► │ chat_app │  (or api.py)
│ (once)   │         │ (CLI test)│          │ (UI)     │
└──────────┘         └──────────┘          └──────────┘
     │                    │                      │
     ▼                    ▼                      ▼
  chroma_db/           Type Qs              Browser at
  appears              in terminal          localhost:8501
```

---

## 🧪 Why use Colab for learning?

Google Colab is a free Jupyter notebook in the cloud. It's perfect
for *learning* this code because:

1. **No installs.** Click "Open in Colab", you're running Python in 5 seconds.
2. **Run cell-by-cell.** Stop after each step, inspect what just happened.
3. **Free GPUs/RAM.** Not needed here, but nice to know.
4. **Shareable.** A single URL = whole tutorial.

For *production* (a real chatbot website), you still need your laptop
or a server — but for understanding, Colab beats everything.

---

## 🚀 How to open the notebook in Colab

### Option A — drag-and-drop (easiest, no GitHub needed)

1. Open <https://colab.research.google.com/>
2. Click **File → Upload notebook**
3. Drag `colab/RaviBot_Learn_In_Colab.ipynb` from your computer
4. Done — start running cells

### Option B — open from GitHub

Once you've pushed `llm_development/` to GitHub:

1. Open <https://colab.research.google.com/>
2. **File → Open notebook → GitHub** tab
3. Paste the repo URL or pick from the list
4. Pick `colab/RaviBot_Learn_In_Colab.ipynb`

---

## 📖 What's inside the notebook

The notebook is split into **4 parts**, each cell explained:

### Part 0 — Setup
- Install packages (`openai`, `chromadb`)
- Paste your OpenAI key
- Create tiny sample data files (so you don't need to upload anything)

### Part 1 — `ingest.py` exposed
Every function from `ingest.py` is split into its own cell:
- `read_file()` — see the raw text
- `chunk_text()` — see the slices
- `embed_texts()` — see the actual 1,536-D vector (truncated)
- `collection.add()` — see the rows in ChromaDB
- A query at the end so you see retrieval working

### Part 2 — `chatbot.py` exposed
- Load the 3 prompts and inspect them
- Run the router on different questions and see PERSONAL vs GENERAL
- Run a personal question end-to-end with print statements at every step
- Run a general question end-to-end
- Compose the whole thing into a single `ask()` function

### Part 3 — FastAPI in Colab
- Define the API
- Run it in the background
- Use `pyngrok` to expose it on a public URL
- Hit `/chat` from a Python `requests` call — see the JSON come back
- (Same code that the chat widget would call)

Total runtime: ~10–15 minutes if you read along.

---

## 🤔 Why is FastAPI a bit weird in Colab?

FastAPI is a *web server* — normally it runs forever and listens for
HTTP requests. Colab's notebook cells expect to finish quickly.

The trick: we run the server in a **background thread** and tunnel it
through **ngrok** so we get a real public HTTPS URL. The notebook
handles this for you — just run the cells.

---

## 🆘 Common Colab issues

| Issue | Fix |
|---|---|
| `Module not found: openai` | The first install cell didn't finish. Run it again. |
| `OPENAI_API_KEY is not set` | Run the cell that sets `os.environ["OPENAI_API_KEY"] = ...` |
| Hung server cell | Colab → Runtime → Restart runtime, then start from Setup |
| ngrok asks for auth token | Sign up free at ngrok.com, paste your token where the notebook asks |
| Hit OpenAI rate limit | Wait 1 minute and retry, or top up credits |

---

## 📚 After Colab — running it on your laptop

When you're done playing in Colab and want the *real* setup:

1. Open `START_HERE.md` in this folder.
2. Follow the 7 steps (Python venv → install → ingest → run).
3. Read `DEEP_DIVE.md` for the comprehensive concept reference.
4. Read `PORTFOLIO_INTEGRATION.md` once you want the chat bubble live.
5. Read `DEPLOYMENT.md` for going to production.

---

Built by Ravi Kiran Pilli · mail2pilliravikiran@gmail.com
