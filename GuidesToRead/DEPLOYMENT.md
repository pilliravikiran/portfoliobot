# 🚀 Deployment Guide — Vercel + Cloudflare + Render

This guide takes RaviBot from "running on my laptop" to "live on the
internet" using free tiers only.

---

## 🧭 The big picture

You have two things to deploy, and they go to different homes:

```
┌──────────────────────────────────────────────────────────────┐
│  Portfolio/                                                  │
│  ├── index.html              ◄── Vercel  OR  Cloudflare Pages│
│  ├── ravibot-widget.js          (your existing static host)  │
│  └── ...                                                     │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS POST /chat
                              ▼
┌──────────────────────────────────────────────────────────────┐
│  llm_development/   (the Python AI brain)                    │
│  ├── api.py                  ◄── Render   (free Python host) │
│  ├── chatbot.py                                              │
│  └── ...                                                     │
└──────────────────────────────────────────────────────────────┘
```

### Why not Vercel for the API?

- Vercel **does** support Python, but only as serverless functions.
- Every request becomes a cold-start: it loads ChromaDB + OpenAI client
  from scratch. That makes each chat 3-5 seconds slower.
- The unzipped function bundle limit is 50 MB; ChromaDB + dependencies
  is close to that.
- It works, but it's a hack. Render gives you a real, warm Python
  process for free.

### Why not Cloudflare Workers for the API?

- Cloudflare Workers run V8 (JS) or Python Workers (beta, very
  limited package support). Our `chromadb` + `openai` Python libraries
  aren't supported. Skip it.

**Verdict:** Static frontend on Vercel/Cloudflare ✅, API on Render ✅.

---

## ✅ Pre-flight: commit everything to GitHub

Both hosts deploy from GitHub. So this is step zero.

### Two folders, two repos

Your two folders live as separate repos (they're independent projects):

- `Portfolio/` → already a git repo with an `origin` remote.
- `llm_development/` → new, needs its own GitHub repo.

### Step A — Push the Portfolio updates

```bash
cd C:\Users\MMS\Documents\Github\Portfolio
git status                            # see what changed
git add index.html ravibot-widget.js
git commit -m "Add RaviBot chat widget"
git push
```

### Step B — Create a new GitHub repo for the AI brain

1. Go to <https://github.com/new>
2. Repo name: `ravibot` (or whatever you like)
3. Set it to **Public** (Render's free tier needs to read it) — or use
   Private if you connect via GitHub App.
4. **Don't** initialise with a README. Click **Create repository**.

GitHub shows you a URL like:
`https://github.com/ravikiranpilli/ravibot.git`

### Step C — Push the AI folder

```bash
cd C:\Users\MMS\Documents\Github\llm_development

git init
git add .
git commit -m "Initial commit: RaviBot AI chatbot"
git branch -M main
git remote add origin https://github.com/ravikiranpilli/ravibot.git
git push -u origin main
```

> 🛡️ **Safety check.** `.gitignore` already excludes `.env`, `venv/`,
> `chroma_db/`, and `node_modules/`. Run `git status` after `git add .`
> and **make sure `.env` is NOT in the list**. If it is, stop and check
> `.gitignore`.

---

## 🐍 Part 1 — Deploy the API to Render (free)

### 1. Create a `start.sh` script

Render needs a start command that (a) builds the vector DB on each cold
boot (because Render's free tier filesystem is ephemeral) and (b) starts
the API.

Create **`llm_development/start.sh`**:

```bash
#!/usr/bin/env bash
set -e
python ingest.py
exec uvicorn api:app --host 0.0.0.0 --port $PORT
```

Commit and push:

```bash
git add start.sh
git commit -m "Add Render start script"
git push
```

### 2. Sign up at Render

- Go to <https://render.com/>
- Sign in with GitHub.

### 3. Create a new Web Service

- Click **New +** → **Web Service**
- Connect your `ravibot` GitHub repo.
- Fill in:

| Field | Value |
|---|---|
| **Name** | `ravibot-api` (becomes part of the URL) |
| **Region** | Closest to you |
| **Branch** | `main` |
| **Runtime** | **Python 3** |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `bash start.sh` |
| **Instance Type** | **Free** |

### 4. Add the secret

Scroll down to **Environment Variables** and add:

| Key | Value |
|---|---|
| `OPENAI_API_KEY` | `sk-...your real key...` |

Click **Create Web Service**.

Render builds and deploys. After ~3 minutes it shows a URL like:

```
https://ravibot-api.onrender.com
```

Verify it's alive:

```
https://ravibot-api.onrender.com/health
```

You should see `{"status":"ok","bot":"RaviBot"}`.

### 5. Free-tier caveats (important)

- **Free Render services sleep after 15 min of no traffic.** The first
  request after sleep takes ~30 seconds (cold start including `ingest.py`).
  After that, requests are fast.
- **Every cold start re-builds the vector DB** (~$0.0002 each time —
  basically nothing).
- To remove the sleep, upgrade to Render's paid tier ($7/mo) **or** use
  a free uptime pinger like UptimeRobot to ping `/health` every 14 min.

---

## 🌐 Part 2 — Point the widget at the deployed API

Edit **`Portfolio/ravibot-widget.js`**, line 26:

```js
const CONFIG = {
  API_URL: "https://ravibot-api.onrender.com/chat",  // ← your Render URL
  ...
};
```

Commit and push:

```bash
cd C:\Users\MMS\Documents\Github\Portfolio
git add ravibot-widget.js
git commit -m "Point widget at production API"
git push
```

---

## 🔒 Part 3 — Tighten CORS

Right now `api.py` allows requests from any website. Lock it to just
your portfolio.

Edit **`llm_development/api.py`**, find the CORS block and replace:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    ...
)
```

with your actual domains:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ravikiranpilli.com",
        "https://www.ravikiranpilli.com",
        "https://ravibot-portfolio.vercel.app",   # if you use vercel preview URLs
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Push it:

```bash
cd C:\Users\MMS\Documents\Github\llm_development
git add api.py
git commit -m "Tighten CORS to portfolio domain only"
git push
```

Render auto-redeploys when it sees the push.

---

## 🅰️ Part 4A — Deploy the Portfolio to **Vercel**

If you already use Vercel for the portfolio, just push to GitHub — Vercel
auto-deploys.

If this is the first time:

1. Go to <https://vercel.com/new>
2. Import the `Portfolio` repo.
3. **Framework Preset:** *Other* (it's static HTML).
4. **Root Directory:** `.` (leave default).
5. **Build Command:** leave empty.
6. **Output Directory:** leave empty (Vercel serves files as-is).
7. Click **Deploy**.

After ~30 seconds you get a URL like
`https://ravibot-portfolio.vercel.app`. Open it → the chat bubble
should appear, click it, ask a question.

### Custom domain (optional)

In the Vercel dashboard: **Settings → Domains → Add** →
`ravikiranpilli.com`. Vercel gives you DNS records to add at your
domain registrar (or at Cloudflare if you use it for DNS — see below).

---

## 🅱️ Part 4B — Deploy the Portfolio to **Cloudflare Pages**

1. Go to <https://dash.cloudflare.com/> → **Workers & Pages** → **Create**.
2. Select **Pages** tab → **Connect to Git** → pick `Portfolio` repo.
3. Set up:

| Field | Value |
|---|---|
| **Project name** | `ravibot-portfolio` |
| **Production branch** | `main` |
| **Framework preset** | *None* |
| **Build command** | *(leave blank)* |
| **Build output directory** | `/` |

4. Click **Save and Deploy**.

After ~1 minute you get
`https://ravibot-portfolio.pages.dev`. The chat bubble works the same
way (it just calls your Render API).

### Using Cloudflare for DNS / custom domain

If your domain is already on Cloudflare, point it at Pages:
**Pages → Custom domains → Set up a custom domain → `ravikiranpilli.com`**.
Cloudflare auto-configures the DNS.

---

## 🔄 Part 5 — How updates flow after deploy

```
You edit a file locally
        │
        ▼
git commit + git push
        │
        ├──────► Portfolio repo ───► Vercel/Cloudflare auto-rebuilds (~30 sec)
        │
        └──────► ravibot repo  ───► Render auto-rebuilds (~3 min)
```

That's it. After this first setup, every change is just commit + push.

---

## ✅ Final smoke test checklist

After deploying, open your live portfolio URL and verify:

- [ ] Page loads (no broken styles).
- [ ] Floating 💬 bubble appears in the bottom-right corner.
- [ ] Clicking it opens the chat panel.
- [ ] Browser DevTools (F12 → Network tab) shows the request hitting
      `https://ravibot-api.onrender.com/chat` — **not** `localhost`.
- [ ] First chat after the API has been idle takes ~30s (cold start);
      every subsequent chat is fast.
- [ ] "Who is Ravi?" returns a real answer with source citations.
- [ ] "What's 2+2?" returns "4" (general questions work too).
- [ ] No CORS errors in the browser console.

---

## 🆘 Common deploy issues

| Symptom | Cause | Fix |
|---|---|---|
| 401 / 403 from API | `OPENAI_API_KEY` not set in Render dashboard | Render → Service → Environment → add var → save → redeploy |
| Widget shows but won't chat | Wrong `API_URL` in `ravibot-widget.js` | Edit, push; Vercel/CF redeploys auto |
| CORS error in browser console | Domain not in `allow_origins` list | Add it to `api.py`, push, wait for Render redeploy |
| Render build fails on `chromadb` | Python version mismatch | Add `runtime.txt` with `python-3.11.9` |
| First request after a while takes 30s | Free-tier sleep | Use UptimeRobot to ping `/health` every 14 min — or upgrade |
| "No knowledge base found" | `ingest.py` didn't run | `start.sh` should call it; check Render logs |

---

## 💸 Total monthly cost

| Service | Cost |
|---|---|
| Vercel / Cloudflare Pages (Portfolio) | **$0** (free forever) |
| Render free tier (API) | **$0** (sleeps after 15 min idle) |
| OpenAI API usage (~1500 chats) | **~$1** |
| **TOTAL** | **~$1/month** |

If you want zero sleep + faster cold starts → Render Starter $7/mo, or
move the API to Fly.io / Railway / Azure Container Apps.

---

Built by Ravi Kiran Pilli · mail2pilliravikiran@gmail.com
