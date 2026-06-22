#!/usr/bin/env python3
"""CLI test runner — no Streamlit required."""
from langchain_core.messages import HumanMessage, AIMessage

from orchestrator.graph import build_graph
from agents.registry import discover_agents


def main() -> None:
    registry = discover_agents()
    if not registry:
        print("No agents found. Check that agents/ modules are importable.")
        return

    graph = build_graph(registry)
    print(f"Personal AI Network — agents loaded: {', '.join(registry.keys())}")
    print("Type 'quit' to exit.\n")

    history: list = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            break

        history.append(HumanMessage(content=user_input))

        result = graph.invoke({
            "messages": history,
            "selected_agent": "",
            "agent_response": "",
        })

        reply      = result["messages"][-1].content
        agent_used = result.get("selected_agent", "none")

        print(f"\nAssistant [{agent_used}]: {reply}\n")
        history.append(AIMessage(content=reply))


if __name__ == "__main__":
    main()
