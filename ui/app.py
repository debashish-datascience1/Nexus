import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from orchestrator.graph import build_graph
from agents.registry import discover_agents
from memory.store import save_message, load_recent, clear_history

st.set_page_config(
    page_title="Personal AI Network",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Personal AI Network")


@st.cache_resource
def get_graph():
    registry = discover_agents()
    graph = build_graph(registry)
    return graph, registry


graph, registry = get_graph()
agent_list = ", ".join(registry.keys()) if registry else "none loaded"
st.caption(f"Active agents: {agent_list}")

with st.sidebar:
    st.header("Agents")
    for name, agent in registry.items():
        st.markdown(f"**{name}**  \n{agent.description}")
    st.divider()
    if st.button("Clear conversation history"):
        clear_history()
        st.session_state.messages = []
        st.rerun()

# Load history from DB on first run
if "messages" not in st.session_state:
    history = load_recent(20)
    st.session_state.messages = [
        {"role": m["role"], "content": m["content"]} for m in history
    ]

# Render existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle new input
if prompt := st.chat_input("Ask anything — news, GitHub, LinkedIn..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
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

        st.markdown(reply)
        if agent_used and agent_used != "none":
            st.caption(f"↳ {agent_used} agent")

    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_message("assistant", reply, agent=agent_used)
