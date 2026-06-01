// Creatrix AI — floating assistant orb (chat + ElevenLabs voice).
// Self-contained: works on every page, with or without config.js.
(function () {
  "use strict";

  function apiBase() {
    if (window.API_BASE) return window.API_BASE;
    const h = window.location.hostname;
    if (h === "localhost" || h === "127.0.0.1") return "http://localhost:8080";
    return window.location.origin;
  }
  const API = apiBase();

  let currentAudio = null;
  let lastReply = "";
  let voicePrep = null;   // in-flight Promise<blobUrl|null> for the latest reply
  let voiceUrl = null;    // resolved blob URL, ready to play with zero delay
  let voiceId = null;     // chosen LIVE from the backend; null → backend default
  const history = [];

  // No hardcoded voices — pull the live ElevenLabs voice list from the backend
  // and use the first one. If this fails we simply omit voice_id and the
  // backend picks its default.
  (async function loadVoices() {
    try {
      const r = await fetch(`${API}/api/v1/virality/voices`);
      if (!r.ok) return;
      const d = await r.json();
      if (d && Array.isArray(d.voices) && d.voices.length && d.voices[0].id) {
        voiceId = d.voices[0].id;
      }
    } catch (_) {}
  })();

  // ── Styles ────────────────────────────────────────────────────────────
  const css = `
  #cx-orb{position:fixed;bottom:70px;right:24px;width:60px;height:60px;border-radius:50%;
    background:radial-gradient(circle at 30% 30%,#a78bfa,#6d5cfc 55%,#4F8EF7);cursor:pointer;z-index:100000;
    box-shadow:0 8px 30px rgba(109,92,252,.55);display:flex;align-items:center;justify-content:center;
    transition:transform .2s ease;animation:cxpulse 2.6s ease-in-out infinite;border:none;}
  #cx-orb:hover{transform:scale(1.08);}
  #cx-orb.speaking{animation:cxspeak .6s ease-in-out infinite;}
  #cx-orb svg{width:26px;height:26px;color:#fff;}
  @keyframes cxpulse{0%,100%{box-shadow:0 8px 30px rgba(109,92,252,.45);}50%{box-shadow:0 8px 42px rgba(109,92,252,.85);}}
  @keyframes cxspeak{0%,100%{transform:scale(1);}50%{transform:scale(1.14);}}
  #cx-panel{position:fixed;bottom:140px;right:24px;width:350px;max-width:calc(100vw - 32px);height:460px;
    max-height:calc(100vh - 180px);background:#0f1117;border:1px solid #2a2f3a;border-radius:18px;z-index:100000;
    display:none;flex-direction:column;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,.5);
    font-family:-apple-system,Segoe UI,Roboto,sans-serif;}
  #cx-panel.open{display:flex;}
  #cx-head{padding:14px 16px;background:linear-gradient(135deg,#6d5cfc,#4F8EF7);color:#fff;display:flex;
    align-items:center;justify-content:space-between;}
  #cx-head b{font-size:14px;font-weight:600;}
  #cx-head .cx-sub{font-size:11px;opacity:.85;}
  #cx-head .cx-actions{display:flex;gap:8px;align-items:center;}
  #cx-head button{background:rgba(255,255,255,.18);border:none;color:#fff;width:28px;height:28px;border-radius:8px;
    cursor:pointer;font-size:13px;display:flex;align-items:center;justify-content:center;}
  #cx-msgs{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:10px;background:#0f1117;}
  .cx-msg{max-width:85%;padding:9px 12px;border-radius:14px;font-size:13px;line-height:1.45;white-space:pre-wrap;}
  .cx-user{align-self:flex-end;background:#6d5cfc;color:#fff;border-bottom-right-radius:4px;}
  .cx-bot{align-self:flex-start;background:#1c2030;color:#e6e8ee;border-bottom-left-radius:4px;}
  .cx-typing{align-self:flex-start;color:#8a90a2;font-size:12px;}
  #cx-input-row{display:flex;gap:8px;padding:12px;border-top:1px solid #2a2f3a;background:#0f1117;}
  #cx-input{flex:1;background:#1c2030;border:1px solid #2a2f3a;border-radius:10px;color:#e6e8ee;padding:9px 12px;
    font-size:13px;outline:none;}
  #cx-send{background:#6d5cfc;border:none;color:#fff;border-radius:10px;padding:0 14px;cursor:pointer;font-size:13px;font-weight:600;}
  #cx-send:disabled{opacity:.5;cursor:default;}`;
  const styleEl = document.createElement("style");
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  // ── Orb button ──────────────────────────────────────────────────────────
  const orb = document.createElement("button");
  orb.id = "cx-orb";
  orb.title = "Ask Creatrix AI";
  orb.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>`;
  document.body.appendChild(orb);

  // ── Panel ─────────────────────────────────────────────────────────────
  const panel = document.createElement("div");
  panel.id = "cx-panel";
  panel.innerHTML = `
    <div id="cx-head">
      <div>
        <b>Creatrix Assistant</b>
        <div class="cx-sub">Ask about scores, trends, content…</div>
      </div>
      <div class="cx-actions">
        <button id="cx-voice" title="Play last reply aloud">🔊</button>
        <button id="cx-close" title="Close">✕</button>
      </div>
    </div>
    <div id="cx-msgs"></div>
    <div id="cx-input-row">
      <input id="cx-input" type="text" placeholder="Type your question…" autocomplete="off"/>
      <button id="cx-send">Send</button>
    </div>`;
  document.body.appendChild(panel);

  const msgs = panel.querySelector("#cx-msgs");
  const input = panel.querySelector("#cx-input");
  const sendBtn = panel.querySelector("#cx-send");
  const voiceBtn = panel.querySelector("#cx-voice");

  function addMsg(text, who) {
    const d = document.createElement("div");
    d.className = "cx-msg " + (who === "user" ? "cx-user" : "cx-bot");
    d.textContent = text;
    msgs.appendChild(d);
    msgs.scrollTop = msgs.scrollHeight;
    return d;
  }

  let greeted = false;
  function openPanel() {
    panel.classList.add("open");
    if (!greeted) {
      addMsg("Hi! I'm your Creatrix AI assistant. Ask me to explain a score, find trends, or help you generate content. Try: \"How does the Ratefluencer Score work?\"", "bot");
      greeted = true;
    }
    input.focus();
  }
  orb.addEventListener("click", () => {
    panel.classList.contains("open") ? panel.classList.remove("open") : openPanel();
  });
  panel.querySelector("#cx-close").addEventListener("click", () => panel.classList.remove("open"));
  // Voice plays ONLY when the user clicks this button — never automatically.
  // The audio is pre-generated the moment the reply arrives (see prepareVoice),
  // so clicking 🔊 plays instantly with no perceptible delay.
  voiceBtn.addEventListener("click", () => {
    if (currentAudio && !currentAudio.paused) {
      currentAudio.pause();
      orb.classList.remove("speaking");
      return;
    }
    speak();
  });

  // Kick off ElevenLabs synthesis as soon as a reply lands so the MP3 is ready
  // before the user ever clicks 🔊. Returns a Promise that resolves to a blob URL.
  function prepareVoice(text) {
    voiceUrl = null;
    voicePrep = (async () => {
      if (!text) return null;
      try {
        const body = { script_text: text.slice(0, 500) };
        if (voiceId) body.voice_id = voiceId;   // live voice; else backend default
        const r = await fetch(`${API}/api/v1/virality/voiceover`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        if (!r.ok) return null;
        const d = await r.json();
        if (!d.audio_base64) return null;
        const bytes = Uint8Array.from(atob(d.audio_base64), (c) => c.charCodeAt(0));
        voiceUrl = URL.createObjectURL(new Blob([bytes], { type: "audio/mpeg" }));
        return voiceUrl;
      } catch (_) {
        return null;
      }
    })();
    return voicePrep;
  }

  async function speak() {
    // Use the pre-generated clip if ready; otherwise await the in-flight job;
    // as a last resort, synthesize now for whatever the last reply was.
    let url = voiceUrl;
    if (!url && voicePrep) url = await voicePrep;
    if (!url && lastReply) url = await prepareVoice(lastReply);
    if (!url) return;
    if (currentAudio) currentAudio.pause();
    currentAudio = new Audio(url);
    orb.classList.add("speaking");
    currentAudio.onended = () => orb.classList.remove("speaking");
    currentAudio.play().catch(() => orb.classList.remove("speaking"));
  }

  async function send() {
    const text = input.value.trim();
    if (!text) return;
    addMsg(text, "user");
    history.push({ role: "user", content: text });
    input.value = "";
    sendBtn.disabled = true;
    const typing = document.createElement("div");
    typing.className = "cx-typing";
    typing.textContent = "Creatrix is thinking…";
    msgs.appendChild(typing);
    msgs.scrollTop = msgs.scrollHeight;
    try {
      const r = await fetch(`${API}/api/v1/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history: history.slice(-8) }),
      });
      typing.remove();
      const d = r.ok ? await r.json() : null;
      const reply = (d && d.reply) ? d.reply : "Sorry, I couldn't reach the assistant. Please try again.";
      addMsg(reply, "bot");
      history.push({ role: "assistant", content: reply });
      lastReply = reply;
      prepareVoice(reply);  // pre-generate now so 🔊 plays with zero delay (still on-demand)
    } catch (_) {
      typing.remove();
      addMsg("Network error — please try again.", "bot");
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  }
  sendBtn.addEventListener("click", send);
  input.addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });
})();
