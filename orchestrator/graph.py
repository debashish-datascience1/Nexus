from typing import Annotated, Literal
from typing_extensions import TypedDict

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from config import GOOGLE_API_KEY, MODEL_NAME


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    selected_agent: str
    agent_response: str


def build_graph(agent_registry: dict):
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.1,
    )

    agent_descriptions = "\n".join(
        f"- {name}: {agent.description}"
        for name, agent in agent_registry.items()
    )

    ROUTER_PROMPT = f"""You are a routing agent. Your only job is to read the user's message and return the name of the best specialist agent to handle it.

Available agents:
{agent_descriptions}

Rules:
- Reply with ONLY the agent name (e.g. "news", "github", "linkedin").
- If the question is general or doesn't match any agent, reply with "none".
- No explanation, no punctuation — just the agent name."""

    def supervisor(state: AgentState) -> dict:
        last_message = state["messages"][-1].content
        response = llm.invoke([
            SystemMessage(content=ROUTER_PROMPT),
            HumanMessage(content=last_message),
        ])
        selected = response.content.strip().lower().split()[0].rstrip(".,!")
        if selected not in agent_registry:
            selected = "none"
        return {"selected_agent": selected, "agent_response": ""}

    def run_agent(state: AgentState) -> dict:
        agent_name = state["selected_agent"]
        query = state["messages"][-1].content

        if agent_name == "none" or agent_name not in agent_registry:
            response = llm.invoke(state["messages"])
            return {"agent_response": response.content, "selected_agent": "none"}

        try:
            raw = agent_registry[agent_name].run(query)
        except Exception as e:
            raw = f"The {agent_name} agent encountered an error: {e}"

        return {"agent_response": raw}

    def synthesizer(state: AgentState) -> dict:
        agent_name = state["selected_agent"]
        raw_data   = state["agent_response"]
        query      = state["messages"][-1].content

        if agent_name == "none":
            return {"messages": [AIMessage(content=raw_data)]}

        synth_prompt = (
            f"The user asked: {query}\n\n"
            f"The {agent_name} agent returned this data:\n{raw_data}\n\n"
            "Write a clear, conversational reply. "
            "Present the information helpfully — use bullet points or bold text where it aids readability. "
            "Be concise. Do not mention the internal agent name."
        )
        response = llm.invoke([HumanMessage(content=synth_prompt)])
        return {"messages": [AIMessage(content=response.content)]}

    graph = StateGraph(AgentState)
    graph.add_node("supervisor", supervisor)
    graph.add_node("run_agent",  run_agent)
    graph.add_node("synthesizer", synthesizer)

    graph.set_entry_point("supervisor")
    graph.add_edge("supervisor",  "run_agent")
    graph.add_edge("run_agent",   "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph.compile()
