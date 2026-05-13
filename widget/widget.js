/* ============================================================
 * RaviBot — embeddable chat widget for the Portfolio
 * ------------------------------------------------------------
 * Drop this on any page with:
 *     <script src="ravibot-widget.js" defer></script>
 *
 * It creates:
 *   - A floating round chat bubble in the bottom-right corner.
 *   - A chat panel that opens when you click the bubble.
 *   - POSTs to the FastAPI backend at CONFIG.API_URL.
 *
 * To run the backend locally (in another terminal):
 *     cd llm_development
 *     uvicorn api:app --port 8000
 *
 * When you deploy the API to Render / Railway / Azure etc.,
 * just change CONFIG.API_URL below.
 * ============================================================ */
(function () {
  "use strict";

  // -----------------------------------------------------------
  // CONFIG — change this when you deploy
  // -----------------------------------------------------------
  const CONFIG = {
    API_URL: "http://localhost:8000/chat",   // <-- change to your deployed API
    BOT_NAME: "PortfolioBot",
    GREETING:
      "Hi 👋 I'm PortfolioBot — ask me anything about Ravi (skills, experience, projects, contact) or just chat about anything else!",
    PRIMARY: "linear-gradient(135deg,#0071e3,#5856d6)",
    POSITION: { right: "24px", bottom: "24px" },
  };

  // -----------------------------------------------------------
  // 1. Inject CSS once
  // -----------------------------------------------------------
  const css = `
    .rb-fab {
      position: fixed; right: ${CONFIG.POSITION.right};
      bottom: ${CONFIG.POSITION.bottom};
      width: 60px; height: 60px; border-radius: 50%;
      background: ${CONFIG.PRIMARY};
      box-shadow: 0 6px 22px rgba(0,113,227,.35);
      cursor: pointer; z-index: 99999;
      display: flex; align-items: center; justify-content: center;
      color: #fff; font-size: 26px; border: none;
      transition: transform .25s ease, box-shadow .25s ease;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    .rb-fab:hover { transform: scale(1.08); }
    .rb-fab .rb-pulse {
      position: absolute; inset: -6px; border-radius: 50%;
      border: 2px solid rgba(88,86,214,.45);
      animation: rbPulse 2.2s ease-out infinite;
      pointer-events: none;
    }
    @keyframes rbPulse {
      0%   { transform: scale(.9); opacity: .8; }
      100% { transform: scale(1.35); opacity: 0; }
    }
    .rb-panel {
      position: fixed; right: ${CONFIG.POSITION.right};
      bottom: calc(${CONFIG.POSITION.bottom} + 76px);
      width: 380px; max-width: calc(100vw - 32px);
      height: 560px; max-height: calc(100vh - 120px);
      background: #fff; border-radius: 18px;
      box-shadow: 0 14px 48px rgba(0,0,0,.18);
      z-index: 99999; display: none; flex-direction: column;
      overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      border: 1px solid rgba(0,0,0,.06);
    }
    .rb-panel.open { display: flex; animation: rbFadeIn .25s ease; }
    @keyframes rbFadeIn {
      from { opacity: 0; transform: translateY(8px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    .rb-head {
      padding: 14px 16px; color: #fff;
      background: ${CONFIG.PRIMARY};
      display: flex; align-items: center; justify-content: space-between;
    }
    .rb-head h4 { margin: 0; font-size: 15px; font-weight: 600; letter-spacing: .2px; }
    .rb-head .sub { font-size: 11px; opacity: .85; margin-top: 2px; }
    .rb-head button {
      background: rgba(255,255,255,.2); border: none; color: #fff;
      width: 28px; height: 28px; border-radius: 50%;
      cursor: pointer; font-size: 16px; transition: background .2s;
    }
    .rb-head button:hover { background: rgba(255,255,255,.35); }
    .rb-msgs {
      flex: 1; overflow-y: auto; padding: 16px;
      background: #fafafa; display: flex; flex-direction: column; gap: 10px;
    }
    .rb-bubble {
      max-width: 85%; padding: 10px 14px; border-radius: 16px;
      font-size: 14px; line-height: 1.45; white-space: pre-wrap; word-wrap: break-word;
    }
    .rb-bubble.user { align-self: flex-end; background: #0071e3; color: #fff; border-bottom-right-radius: 4px; }
    .rb-bubble.bot  { align-self: flex-start; background: #fff; color: #1d1d1f;
      border-bottom-left-radius: 4px; border: 1px solid #e5e5ea; }
    .rb-bubble.bot .sources {
      display: block; font-size: 11px; color: #888; margin-top: 6px;
    }
    .rb-suggest {
      display: flex; flex-wrap: wrap; gap: 6px; padding: 6px 12px 0;
    }
    .rb-suggest button {
      font-size: 12px; padding: 6px 10px; border-radius: 999px;
      background: #f0f4ff; color: #0b5ed7; border: 1px solid #d6e4ff;
      cursor: pointer; transition: all .2s;
      font-family: inherit;
    }
    .rb-suggest button:hover { background: #e0eaff; transform: translateY(-1px); }
    .rb-form {
      display: flex; padding: 10px; border-top: 1px solid #eee;
      background: #fff; gap: 8px;
    }
    .rb-form input {
      flex: 1; padding: 10px 12px; border-radius: 999px;
      border: 1px solid #d2d2d7; font-size: 14px; outline: none;
      font-family: inherit;
    }
    .rb-form input:focus { border-color: #0071e3; }
    .rb-form button {
      border: none; padding: 0 16px; border-radius: 999px;
      background: ${CONFIG.PRIMARY}; color: #fff;
      font-weight: 600; cursor: pointer; font-family: inherit;
    }
    .rb-form button:disabled { opacity: .5; cursor: wait; }
    .rb-typing {
      font-size: 12px; color: #6e6e73; padding: 0 16px 8px; font-style: italic;
    }
  `;
  const styleEl = document.createElement("style");
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  // -----------------------------------------------------------
  // 2. Build DOM
  // -----------------------------------------------------------
  const fab = document.createElement("button");
  fab.className = "rb-fab";
  fab.setAttribute("aria-label", "Open chat with RaviBot");
  fab.innerHTML = `<span class="rb-pulse"></span>💬`;
  document.body.appendChild(fab);

  const panel = document.createElement("div");
  panel.className = "rb-panel";
  panel.innerHTML = `
    <div class="rb-head">
      <div>
        <h4>🤖 ${CONFIG.BOT_NAME}</h4>
        <div class="sub">AI assistant · ask me anything</div>
      </div>
      <button class="rb-close" aria-label="Close">✕</button>
    </div>
    <div class="rb-msgs"></div>
    <div class="rb-suggest"></div>
    <div class="rb-typing" style="display:none">RaviBot is typing…</div>
    <form class="rb-form" autocomplete="off">
      <input type="text" placeholder="Ask anything..." required>
      <button type="submit">Send</button>
    </form>
  `;
  document.body.appendChild(panel);

  const msgsEl    = panel.querySelector(".rb-msgs");
  const suggestEl = panel.querySelector(".rb-suggest");
  const formEl    = panel.querySelector(".rb-form");
  const inputEl   = panel.querySelector("input");
  const sendBtn   = panel.querySelector(".rb-form button");
  const typing    = panel.querySelector(".rb-typing");
  const closeBtn  = panel.querySelector(".rb-close");

  // -----------------------------------------------------------
  // 3. State
  // -----------------------------------------------------------
  const history = []; // {role, content}
  let opened = false;

  const SUGGESTIONS = [
    "Who is Ravi?",
    "What's his strongest tech stack?",
    "Tell me about his projects",
    "How can I contact him?",
  ];

  function renderSuggestions() {
    suggestEl.innerHTML = "";
    SUGGESTIONS.forEach((s) => {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = s;
      b.addEventListener("click", () => {
        inputEl.value = s;
        formEl.dispatchEvent(new Event("submit", { cancelable: true }));
      });
      suggestEl.appendChild(b);
    });
  }

  function addBubble(text, who, sources) {
    const div = document.createElement("div");
    div.className = `rb-bubble ${who}`;
    div.textContent = text;
    if (sources && sources.length) {
      const s = document.createElement("span");
      s.className = "sources";
      s.textContent = "Sources: " + sources.join(", ");
      div.appendChild(s);
    }
    msgsEl.appendChild(div);
    msgsEl.scrollTop = msgsEl.scrollHeight;
  }

  function open() {
    panel.classList.add("open");
    setTimeout(() => inputEl.focus(), 100);
    if (!opened) {
      addBubble(CONFIG.GREETING, "bot");
      renderSuggestions();
      opened = true;
    }
  }
  function close() { panel.classList.remove("open"); }

  fab.addEventListener("click", () => {
    panel.classList.contains("open") ? close() : open();
  });
  closeBtn.addEventListener("click", close);

  // -----------------------------------------------------------
  // 4. Submit a question
  // -----------------------------------------------------------
  formEl.addEventListener("submit", async (e) => {
    e.preventDefault();
    const q = inputEl.value.trim();
    if (!q) return;
    inputEl.value = "";
    sendBtn.disabled = true;
    suggestEl.innerHTML = ""; // hide suggestions after first question

    addBubble(q, "user");
    history.push({ role: "user", content: q });
    typing.style.display = "block";

    try {
      const resp = await fetch(CONFIG.API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q, history }),
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      addBubble(data.answer, "bot", data.sources);
      history.push({ role: "assistant", content: data.answer });
    } catch (err) {
      addBubble(
        "Sorry — I couldn't reach the server. Make sure the FastAPI backend is running (cd llm_development && uvicorn api:app --port 8000).",
        "bot"
      );
      console.error("RaviBot error:", err);
    } finally {
      typing.style.display = "none";
      sendBtn.disabled = false;
      inputEl.focus();
    }
  });
})();
