# 🤖 Apex Support Bot - AI Customer Service Agent

An intelligent customer support agent built with **Streamlit**, **DeepSeek API**, and **OpenAI SDK**, featuring function calling for order lookups, automated refunds, and system guardrails.

---

## 🌟 Key Features
* **Function Calling**: Automatically queries simulated backend databases for order statuses and execution of refund logic.
* **Smart Business Logic**: Automated date and window checking for return policies (<= 14 days).
* **Robust Guardrails**: Built-in system prompt instructions to defend against prompt injection and unauthorized compensation requests.
* **Interactive UI**: Clean and intuitive chat interface built using Streamlit.

---

## 🛠️ Tech Stack
* **Language**: Python 3.10+
* **Frontend/Framework**: Streamlit
* **LLM Provider**: DeepSeek API (`deepseek-v4-flash`) via OpenAI Python SDK
* **Tooling**: GitHub Copilot, VS Code

---

## 🚀 Getting Started

### 1. Prerequisites & Installation
Clone the repository and install requirements:
```bash
git clone [https://github.com/your-username/apex-support-bot.git](https://github.com/your-username/apex-support-bot.git)
cd apex-support-bot
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install streamlit openai python-dotenv