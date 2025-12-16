# 🤖 AI Prompt Analyzer & Tool Finder

An intelligent platform that analyzes **any user prompt (even bad or vague ones)** and recommends the **most suitable AI tools** across domains like **Text, Image, Audio, Video, Code, Productivity, and Data**.

This project uses:
- Prompt rewriting
- Intent extraction
- Semantic embeddings
- Tool similarity matching
- Local LLM support (Ollama)
- Clean web UI with chatbot support

---

## 🚀 Features

- 🔍 **Prompt Analysis**
  - Works even with badly structured prompts
  - Rewrites prompts into a clean, usable form
  - Extracts intent automatically

- 🧠 **AI Tool Recommendation**
  - Matches prompts with the best AI tools
  - Uses vector embeddings + cosine similarity
  - Confidence score for recommendations

- 🛠 **Tool Details**
  - Click any tool to view:
    - Description
    - Domain
    - Use cases
    - Pricing
    - Official website

- 💬 **Ask AI Chatbot**
  - Chat with an AI assistant inside the UI
  - Copy responses easily

- 🎙 **Voice Input (Browser)**
  - Convert voice → prompt using Web Speech API

- 🧩 **Tool Comparator**
  - Select multiple tools and compare features

- 🛡 **Moderation & Safety**
  - Filters unsafe or restricted prompts
  - Logs low-quality or unclear prompts for learning

---

## 🧱 Tech Stack

### Backend
- **Python**
- **FastAPI**
- **NumPy**
- **Ollama (Local LLM + Embeddings)**
- **nomic-embed-text**

### Frontend
- **HTML + CSS**
- **Vanilla JavaScript**
- **Fetch API**
- **Web Speech API (Voice input)**

---

## 📁 Project Structure