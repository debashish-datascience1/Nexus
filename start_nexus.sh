#!/usr/bin/env bash
# Launch Nexus AI and open the browser after the server is ready

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$PROJECT_DIR/venv/bin/activate"
PORT=8501

# Start Streamlit in the background
source "$VENV"
streamlit run "$PROJECT_DIR/ui/app.py" \
  --server.port $PORT \
  --server.headless true \
  --browser.gatherUsageStats false \
  &> "$PROJECT_DIR/nexus.log" &

# Wait until the server is up (max 15 s)
for i in $(seq 1 15); do
  sleep 1
  if curl -s "http://localhost:$PORT" >/dev/null 2>&1; then
    break
  fi
done

# Open browser — Streamlit loading the page triggers the voice greeting
xdg-open "http://localhost:$PORT" 2>/dev/null || \
  google-chrome "http://localhost:$PORT" 2>/dev/null || \
  firefox "http://localhost:$PORT" 2>/dev/null
