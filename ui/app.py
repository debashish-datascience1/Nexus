import sys
import os
import re
import json
import html as _html
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components
from langchain_core.messages import HumanMessage, AIMessage

from orchestrator.graph import build_graph
from agents.registry import discover_agents
from memory.store import save_message, load_recent, clear_history

st.set_page_config(
    page_title="Personal AI Network",
    page_icon="🤖",
    layout="wide",
)

# ── Text-to-speech (browser Web Speech API — completely free) ─────────────────
def _strip_for_tts(text: str) -> str:
    text = re.sub(r"\*+", "", text)
    text = re.sub(r"#+\s*", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r"\n+", ". ", text)
    return text.strip()


def _speak(text: str) -> None:
    """Inject a zero-height iframe that speaks text via the browser's speech API."""
    clean = _strip_for_tts(text)
    if not clean:
        return
    payload = json.dumps(clean)   # handles all escaping
    components.html(f"""
    <script>
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance({payload});
      u.rate  = 0.93;
      u.pitch = 1.05;
      u.volume = 1.0;
      window.speechSynthesis.speak(u);
    </script>
    """, height=0, scrolling=False)


# ── Card colour palette (cycles per article) ──────────────────────────────────
_GRADIENTS = [
    "linear-gradient(135deg,#667eea,#764ba2)",
    "linear-gradient(135deg,#f093fb,#f5576c)",
    "linear-gradient(135deg,#4facfe,#00f2fe)",
    "linear-gradient(135deg,#43e97b,#38f9d7)",
    "linear-gradient(135deg,#fa709a,#fee140)",
    "linear-gradient(135deg,#a18cd1,#fbc2eb)",
    "linear-gradient(135deg,#30cfd0,#330867)",
    "linear-gradient(135deg,#f77062,#fe5196)",
    "linear-gradient(135deg,#e0c3fc,#8ec5fc)",
    "linear-gradient(135deg,#fddb92,#d1fdff)",
]

_NEWS_CSS = """
<style>
.nf-title{font-size:20px;font-weight:700;margin:4px 0 18px;display:flex;align-items:center;gap:8px;}
.news-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px;padding-bottom:24px;}
.nc{border-radius:14px;overflow:hidden;background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.08);display:flex;flex-direction:column;
    transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease;}
.nc:hover{transform:translateY(-5px);box-shadow:0 18px 52px rgba(0,0,0,0.38);
          border-color:rgba(255,255,255,0.2);}
.nc-banner{height:90px;display:flex;align-items:flex-end;padding:10px 14px;}
.nc-source{font-size:12px;font-weight:700;color:rgba(255,255,255,.92);
           text-shadow:0 1px 4px rgba(0,0,0,.45);letter-spacing:.4px;
           white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%;}
.nc-body{padding:14px 16px 16px;flex:1;display:flex;flex-direction:column;}
.nc-date{font-size:11px;color:#5c5c5c;margin-bottom:8px;letter-spacing:.4px;}
.nc-title{font-size:14.5px;font-weight:700;line-height:1.45;color:#dcdcdc;margin-bottom:9px;}
.nc-desc{font-size:12.5px;color:#7d7d7d;line-height:1.7;flex:1;
         display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden;}
.nc-link{display:inline-flex;align-items:center;gap:4px;margin-top:13px;
         color:#5b9bd5;font-size:12px;font-weight:600;text-decoration:none;letter-spacing:.3px;}
.nc-link:hover{color:#7db5ef;text-decoration:underline;}
</style>
"""


def _render_news(content: str) -> None:
    try:
        articles = json.loads(content)
    except Exception:
        st.markdown(content)
        return

    if not articles:
        st.info("No news articles found. Try a different or broader query.")
        return

    st.markdown(_NEWS_CSS, unsafe_allow_html=True)
    count = len(articles)
    st.markdown(
        f'<div class="nf-title">📰 {count} article{"s" if count != 1 else ""}</div>',
        unsafe_allow_html=True,
    )

    cards = ['<div class="news-grid">']
    for i, a in enumerate(articles):
        grad  = _GRADIENTS[i % len(_GRADIENTS)]
        title = _html.escape(a.get("title", ""))
        src   = _html.escape(a.get("source", "News"))
        date  = _html.escape((a.get("published") or "")[:10])
        desc  = _html.escape(a.get("description", ""))
        url   = _html.escape(a.get("url", "#"))

        cards.append(f"""
<a href="{url}" target="_blank" style="text-decoration:none;color:inherit;display:block;">
  <div class="nc">
    <div class="nc-banner" style="background:{grad};">
      <span class="nc-source">{src}</span>
    </div>
    <div class="nc-body">
      <div class="nc-date">{date}</div>
      <div class="nc-title">{title}</div>
      <div class="nc-desc">{desc}</div>
      <span class="nc-link">Read full article →</span>
    </div>
  </div>
</a>""")

    cards.append("</div>")
    st.markdown("\n".join(cards), unsafe_allow_html=True)


def _render_message(content: str, agent: str = "") -> None:
    if agent == "news":
        _render_news(content)
    else:
        st.markdown(content)


# ── Bootstrap ─────────────────────────────────────────────────────────────────
@st.cache_resource
def get_graph():
    registry = discover_agents()
    graph = build_graph(registry)
    return graph, registry


graph, registry = get_graph()

st.title("🤖 Personal AI Network")
agent_list = ", ".join(registry.keys()) if registry else "none loaded"
st.caption(f"Active agents: {agent_list}")

with st.sidebar:
    st.header("Agents")
    for name, agent in registry.items():
        st.markdown(f"**{name}**  \n{agent.description}")
    st.divider()
    tts_on = st.toggle("🔊 Read responses aloud", value=False, key="tts_on")
    st.divider()
    if st.button("Clear conversation history"):
        clear_history()
        st.session_state.messages = []
        st.rerun()

# ── Session history ────────────────────────────────────────────────────────────
def _greeting() -> str:
    hour = datetime.now().hour
    if hour < 12:
        period = "Morning"
    elif hour < 17:
        period = "Afternoon"
    else:
        period = "Evening"
    return (
        f"Good {period}, Boss! 👋\n\n"
        "What would you like me to do today? I can fetch **news**, check your **GitHub**, "
        "look up **LinkedIn** profiles, or just have a conversation."
    )

if "messages" not in st.session_state:
    history = load_recent(20)
    st.session_state.messages = [
        {"role": m["role"], "content": m["content"], "agent": m.get("agent") or ""}
        for m in history
    ]
    if not st.session_state.messages:
        greeting = _greeting()
        st.session_state.messages.append(
            {"role": "assistant", "content": greeting, "agent": ""}
        )
        st.session_state["_speak_greeting"] = greeting

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        _render_message(msg["content"], msg.get("agent", ""))

# Speak greeting once on fresh session (after it's rendered above)
if "_speak_greeting" in st.session_state:
    _speak(st.session_state.pop("_speak_greeting"))

# ── Chat input ─────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask anything — news, GitHub, LinkedIn..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "agent": ""})
    save_message("user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(""):
            lc_messages = [
                HumanMessage(content=m["content"]) if m["role"] == "user"
                else AIMessage(content=m["content"])
                for m in st.session_state.messages
            ]
            result = graph.invoke({
                "messages": lc_messages,
                "selected_agent": "",
                "agent_response": "",
            })

        agent_used = result.get("selected_agent", "")
        reply = result["messages"][-1].content

        _render_message(reply, agent_used)
        if agent_used and agent_used != "none":
            st.caption(f"↳ {agent_used} agent")

        if tts_on and agent_used != "news":
            _speak(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply, "agent": agent_used})
    save_message("assistant", reply, agent=agent_used)
