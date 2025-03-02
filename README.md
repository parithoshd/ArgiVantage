# ArgiVantage
# FastAPI Twilio Voice Bot with OpenAI, Deepgram, and LangChain

## Overview

This application is designed specifically for farmers, allowing them to call a dedicated number provided through Twilio to ask any agriculture-related questions. Even in areas with limited or no personal internet access, farmers can simply use a basic phone connection to reach the system, ensuring they have access to valuable, timely information about various agricultural practices.

- **FastAPI:** Serves as the web framework to handle incoming HTTP requests.
- **Twilio:** Manages incoming voice calls and recording via its webhook.
- **OpenAI Whisper API:** Transcribes recorded audio into text.
- **Deepgram (optional alternative):** Can also be used for speech-to-text processing.
- **LangChain & FAISS:** Processes local documents (PDFs and text files) to build a Retrieval-Augmented Generation (RAG) chain, which answers user queries about agriculture.
- **NGROK:** Exposes the local FastAPI server to the public internet for development and testing.

## Features

- **Voice Call Handling:** Uses Twilio to record and process incoming voice calls.
- **Speech-to-Text:** Transcribes audio recordings using OpenAI’s Whisper API.
- **RAG Chain:** Answers agriculture-related questions by retrieving relevant information from local documents using LangChain and FAISS.
- **Dynamic NGROK Tunneling:** Automatically starts an ngrok tunnel for easy public access during development.
- **Document Processing:** Loads and splits PDF and text files from the `documents` directory to build a vector store.

## Requirements

- **Python 3.9** (recommended for FAISS compatibility)
- Twilio Account (with a purchased phone number)
- OpenAI API Key
- Deepgram API Key
- Ngrok Account (for tunneling)

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/fastapi-twilio-voice-bot.git
   cd fastapi-twilio-voice-bot
