# ⚽ PIXEL BUDDY - AI Soccer Rules Assistant

**Pixel Buddy** is an intelligent, domain-specific voice assistant designed to answer questions about soccer rules, FIFA regulations, players, and tournaments. It features a beautiful GUI, advanced Speech-to-Text with noise reduction, and a RAG (Retrieval-Augmented Generation) system to ensure factual accuracy.

## 🌟 Features

-   **Dual Interface**: Beautiful GUI (`customtkinter`) or Command Line mode.
-   **Smart Speech Recognition**: Uses `OpenAI Whisper` with custom noise reduction algorithms.
-   **Soccer Expert**: Specialized knowledge base using official **FIFA Laws of the Game**.
-   **Live Knowledge**: Integrated Wikipedia retrieval for player and team history.
-   **Privacy First**: Runs **Llama 2** locally via Ollama (No API costs, works offline).
-   **RAG Architecture**: Retrieves facts before answering to reduce hallucinations.
-   **Voice Output**: Text-to-Speech (TTS) response for a full voice loop.

## 📋 Prerequisites

-   **Python 3.9** or higher
-   **Ollama** installed and running (for the local AI brain)
-   Microphone & Speakers
-   ~4GB RAM minimum (8GB recommended)

## 🏗️ Architecture

*(Required for Project Documentation)*

The system follows a modular NLP pipeline:
1.  **Input:** User speaks into the microphone.
2.  **STT Module:** Audio is processed by `Whisper` + `NoiseReduce` to generate text.
3.  **Topic Filter:** System checks if the query is soccer-related.
4.  **RAG Retrieval:** Search engine queries `soccer_rules.json` and Wikipedia.
5.  **LLM Inference:** Retrieved context + Query are sent to **Llama 2** (Ollama).
6.  **Output:** Response is displayed in the GUI and spoken via TTS.

## 🚀 Quick Start

### 1. Install Ollama (Required for Local AI)

**Windows / Mac / Linux:**
Download from [ollama.com](https://ollama.com) and install.

Then, open your terminal and run:
```bash
# Pull the Llama 2 model (or Llama 3 if your hardware supports it)
ollama pull llama2
# Clone repository
git clone [https://github.com/your-username/pixel-buddy.git](https://github.com/your-username/pixel-buddy.git)
cd pixel-buddy
# Install dependencies
pip install -r requirements.txt
#Option A: GUI Mode
python main_gui.py
#Option B: Console Mode
python main.py