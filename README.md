# 🏛️ Multi-LLM Political Debate Application

An interactive, real-time web application built with **Gradio** that orchestrates an automated, multi-turn political debate between two distinct Large Language Models powered by different providers:

* **Government Spokesperson:** Powered by **Google Gemini (`gemini-3.5-flash-lite`)**
* **Opposition Leader:** Powered by **Groq (`qwen/qwen3.8-27b`)**

The application takes a target country as input and simulates a dynamic 10-round debate where the Government defends its policies, growth, and social programs, while the Opposition critiques them using alternative counter-statistics.

---

## ✨ Key Features

* **Cross-Provider Architecture:** Demonstrates how to combine Google's GenAI SDK and Groq's API within a single synchronized workflow.
* **Real-Time Streaming UI:** Built with Gradio `yield` statements to stream each round's progression live to the chat interface.
* **Rate-Limit & Quota Resilience:** Includes built-in exponential backoff retries for Gemini and intentional delays (`time.sleep`) between turns to prevent hitting Free Tier rate limits (TPM).
* **Context-Aware Debating:** Feeds recent conversation context into each subsequent model prompt so the LLMs can directly respond to each other's points.

---

## 🛠️ Prerequisites & Tech Stack

* **Python 3.10+**
* **Gradio** (Web UI)
* **Google GenAI SDK** (`google-genai`)
* **Groq SDK** (`groq`)

---

## 🚀 Installation & Setup

### 1. Clone or Download the Repository
Navigate to your project directory.

### 2. Install Dependencies
Install the required Python packages using pip:

```bash
pip install gradio google-genai groq

```

### 3. Set Up API Keys

The application requires API keys from both Google Gemini and Groq. Set them as environment variables in your terminal before running the script:

* **On Linux / macOS:**
```bash
export GEMINI_API_KEY="your-google-gemini-api-key"
export GROQ_API_KEY="your-groq-api-key"

```


* **On Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY="your-google-gemini-api-key"
set GROQ_API_KEY="your-groq-api-key"

```


* **On Windows (PowerShell):**
```powershell
\$env:GEMINI_API_KEY="your-google-gemini-api-key"
\$env:GROQ_API_KEY="your-groq-api-key"

```



---

## 💻 Running the Application

Execute the Python script to launch the local Gradio server:

```bash
python app.py

```

Once running, open the local URL provided in your terminal (usually `http://127.0.0.1:7860`) in your web browser.

---

## ⚙️ Configuration

You can easily modify the application behavior by adjusting the configuration variables at the top of the script:

* **`GEMINI_MODEL`**: Change the Google model (default: `gemini-3.5-flash-lite`).
* **`GROQ_MODEL`**: Change the Groq model (default: `qwen/qwen3.8-27b`).
* **`max_rounds`**: Adjust the total number of debate exchanges inside `run_full_debate()` (default: `10`).
* **`max_messages`**: Control how much conversation history is fed into each turn via `format_recent_context()` (default: `4`).

---
