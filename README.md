# Nexus — Personal AI Agent Network

A personal AI assistant that routes your queries to specialized agents (GitHub, News, LinkedIn) using a LangGraph supervisor architecture powered by Google Gemini.

## How it works

```
User query → Supervisor (Gemini) → routes to best agent → Synthesizer → conversational reply
```

The supervisor reads your message and picks the right specialist. If no agent fits, Gemini answers directly.

## Agents

| Agent | What it does |
|-------|-------------|
| **GitHub** | Open PRs, assigned issues, recent commits |
| **News** | Top headlines and articles via NewsAPI / RSS |
| **LinkedIn** | Connection requests, feed posts, notifications |

## Setup

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/your-username/nexus.git
cd nexus
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_personal_access_token_here
NEWSAPI_KEY=your_newsapi_key_here
LINKEDIN_EMAIL=your_linkedin_email_here
LINKEDIN_PASSWORD=your_linkedin_password_here
```

| Key | Where to get it |
|-----|----------------|
| `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) |
| `GITHUB_TOKEN` | [GitHub → Settings → Developer settings → PAT](https://github.com/settings/tokens) |
| `NEWSAPI_KEY` | [newsapi.org](https://newsapi.org/register) |
| `LINKEDIN_EMAIL` / `LINKEDIN_PASSWORD` | Your LinkedIn credentials |

### 3. Run

**Streamlit UI:**
```bash
PYTHONPATH=. streamlit run ui/app.py
```

**CLI (no browser):**
```bash
python run_cli.py
```

## Project structure

```
nexus/
├── agents/          # Specialist agents (github, news, linkedin)
├── orchestrator/    # LangGraph supervisor + routing graph
├── tools/           # API wrappers (GitHub, NewsAPI, LinkedIn)
├── memory/          # Conversation history store
├── ui/              # Streamlit frontend
├── config.py        # Env config
└── run_cli.py       # CLI entry point
```

## Tech stack

- [LangGraph](https://github.com/langchain-ai/langgraph) — agent orchestration
- [LangChain](https://github.com/langchain-ai/langchain) — LLM tooling
- [Google Gemini](https://ai.google.dev/) (`gemini-2.0-flash`) — LLM backbone
- [Streamlit](https://streamlit.io/) — UI
