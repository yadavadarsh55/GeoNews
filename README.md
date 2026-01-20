# 🌍 AI-Powered Geonews Agent

**An autonomous multi-agent system that researches, analyzes, writes, and publishes a weekly geopolitical newsletter.**

> **Note:** This project is currently a local prototype and has not yet been deployed to a production environment.

## 📖 Overview

This project leverages **CrewAI** and **Google's Gemini 2.5 Flash** to automate the entire lifecycle of a newsletter. Instead of manually searching for news and writing summaries, a team of AI agents collaborates to produce a professional report on geopolitical events (focused on India and the Globe).

It uses the **Model Context Protocol (MCP)** for file system interactions and Pydantic for strict output validation.

## 🤖 The Crew (Agents)

The system is composed of specialized agents, each with a distinct role:

1.  **🕵️ Senior Data Researcher:** Scrapes the web for the latest geopolitical news, filtering for high-impact stories.
2.  **🧠 Geopolitical Analyst:** Synthesizes the raw data, identifying trends and connecting global events to local impacts.
3.  **✍️ Senior Newsletter Writer:** Drafts the newsletter content in an engaging, informative tone.
4.  **✅ Quality Assurance Editor:** Reviews the draft for accuracy, tone, and formatting, ensuring the output is valid JSON.
5.  **bad📧 Chief Publisher:** Converts the final content into an HTML template and handles email distribution (via SMTP).

## 🛠️ Tech Stack

* **Framework:** [CrewAI](https://crewai.com) (Orchestration)
* **LLM:** Google `gemini-2.5-flash` (Optimized for speed and context)
* **Language:** Python 3.12+
* **Package Manager:** `uv` (Fast Python package installer)
* **Tools:**
    * **MCP (Model Context Protocol):** For safe local file handling.
    * **SerperDevTool:** For Google Search capabilities.
    * **Pydantic:** For data validation and structured output.

## ⚙️ Prerequisites

* Python 3.10 or higher
* [uv](https://github.com/astral-sh/uv) installed (recommended)
* API Keys for:
    * **Google Gemini** (LLM)
    * **Serper.dev** (Google Search)
    * **Gmail** (App Password for sending emails)

## 🚀 Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/geonews-agent.git](https://github.com/yourusername/geonews-agent.git)
    cd geonews-agent
    ```

2.  **Install dependencies using `uv`:**
    ```bash
    uv sync
    # OR if you are not using a lockfile yet:
    uv pip install crewai crewai-tools google-generativeai pydantic
    ```

3.  **Set up Environment Variables:**
    Create a `.env` file in the root directory:
    ```env
    # LLM Provider
    GOOGLE_API_KEY=your_gemini_api_key
    MODEL=gemini/gemini-2.5-flash

    # Tools
    SERPER_API_KEY=your_serper_api_key

    # Email Publishing (Optional for testing)
    GMAIL_USER=your_email@gmail.com
    GMAIL_PASS=your_app_password
    ```

## 🏃 Usage

To start the agent workflow locally:

```bash
uv run python main.py
(or)
crewai kickoff main.py
```