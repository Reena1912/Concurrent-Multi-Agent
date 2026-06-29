# Concurrent Fan-Out Multi-Agent Workflow

This project implements a concurrent (fan-out) multi-agent workflow in Python using the **Microsoft Agent Framework** and the **Google Gemini API**. It demonstrates how to execute multiple independent AI agents in parallel to drastically improve application latency.

---

## What Is a Fan-Out Workflow?
A fan-out workflow is a design pattern where a single input is distributed to multiple workers or agents simultaneously.

Instead of sequential execution:
```text
Input ──> Agent 1 ──> Agent 2 ──> Agent 3 ──> Agent 4 ──> Agent 5 (10+ seconds total)
```

We execute concurrently:
```text
             ┌──> HindiTranslator ──┐
             ├──> KannadaTranslator ┤
Input Text ──┼──> FrenchTranslator  ┼──> Combine Outputs (~2-3 seconds total)
             ├──> SentimentAnalyzer ┤
             └──> KeywordExtractor  ──┘
```

This is highly efficient when the tasks do not depend on each other (e.g., translating a sentence to French does not require waiting for sentiment analysis).

---

## Project Structure

```text
Fan-Out Multi-Agent/
├── venv/                 # Local Python virtual environment
├── .env                  # Environment secrets containing GEMINI_API_KEY (Ignored by Git)
├── .gitignore            # Git configuration file to exclude secrets and build files
├── main.py               # The complete 5-agent concurrent workflow
├── step_by_step_demo.py  # Educational file demonstrating single vs. parallel runs
└── requirements.txt      # Project dependencies
```

---

## Setup & Installation

### 1. Clone or Open the Project
Ensure you are in the project root directory:
```powershell
cd "C:\Users\asus\OneDrive\Desktop\Projects\AI Agents\Fan-Out Multi-Agent"
```

### 2. Configure the Virtual Environment
Create and activate a Python virtual environment, then install dependencies:
```powershell
# Create virtual environment
python -m venv venv

# Activate venv (Windows)
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Add Your API Key
Create a `.env` file in the root of the project and add your Google Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

---

## How to Run

### Run the Main Workflow
This script runs 5 agents concurrently using `gemini-3.1-flash-lite`:
```powershell
python main.py
```

### Run the Beginner step-by-step Demo
This script splits the workflow into two milestones (a single-agent run vs. a two-agent parallel run) to demonstrate how the framework functions under the hood:
```powershell
python step_by_step_demo.py
```

---

## Key Highlights & Design Lessons

### 1. Model Configuration (`gemini-3.1-flash-lite`)
We use **`gemini-3.1-flash-lite`** because it has active quota available on the Google AI Studio free tier. Preview and base models like `gemini-2.5-flash` have a strict daily limit of 20 requests per day, which is easily hit when running parallel multi-agent workflows.

### 2. Specific Instruction Boundaries
Each agent is given a specific system prompt. Constraints like `"Return ONLY the translation"` or `"Return JSON only"` ensure clean outputs that can be easily parsed by downstream systems:
```python
sentiment_translator = client.as_agent(
    name="SentimentAnalyzer",
    instructions=(
        "Analyze the sentiment of the given text. "
        'Return JSON only: {"sentiment": "positive|negative|neutral", "confidence": 0.0-1.0, "reason": "..."}'
    ),
)
```

### 3. Non-blocking I/O
The workflow uses `asyncio` and `ConcurrentBuilder` to release control back to Python's event loop during network requests. All 5 requests hit Google's servers at once, meaning the execution speed is determined by the slowest single request:
```python
start = time.time()
events = await workflow.run(text)
elapsed = time.time() - start
```

### 4. Windows Terminal Compatibility
To prevent Windows command terminal crashes (`UnicodeEncodeError`) when printing Hindi and Kannada character sets, the scripts automatically reconfigure stdout to support UTF-8:
```python
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
```
