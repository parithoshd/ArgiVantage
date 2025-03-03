# AgriVantage
# FastAPI Twilio Voice Bot with OpenAI, Deepgram, and LangChain

## Overview

This application is designed specifically for farmers, allowing them to call a dedicated number provided through Twilio to ask any agriculture-related questions. Even in areas with limited or no personal internet access, farmers can simply use a basic phone connection to reach the system, ensuring they have access to valuable, timely information about various agricultural practices.

## Technologies Implemented

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
2. **Install all the required dependancies:**
   ```bash
   pip3 install fastapi uvicorn openai requests python-dotenv twilio langchain langchain-openai langchain-community aiohttp pyngrok PyMuPDF faiss-cpu
3. Sign up for a Twilio account and then purchase a phone number by following Twilio's step-by-step instructions. After obtaining your number, navigate to the "Account Info" section on your dashboard and copy your Account SID and Auth Token.
4. Create a .env file and paste the copies Account SID and Auth Token as:
   ```bash
   TWILIO_ACCOUNT_SID="ACXXXXXXXXXXXXXXXXXXXXXXXXXXX"
   TWILIO_AUTH_TOKEN="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
5. Create an account from OpenAI, go to API Key then create your own API key, copy the api key and save it in .env file.
   ```bash
   OPENAI_API_KEY="ENTER_YOUR_AP_KEY"
6. Create a folder named "documents" and populate it with sample PDF files and research papers focused on agriculture.
7. Install ngrok by first creating an account at ngrok.com. Once registered, go to the "Your Authentication" section, and then execute the command ngrok authtoken YOUR_AUTHTOKEN in your terminal. This command will generate your XML configuration file.
8. Now all your dependencies are install and configured, finally on the commmand line run your FastApi using this command:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
9. Your .env file will be updated with an NGROK_URL. Copy that URL and head over to your Twilio Console. Under Develop > Phone Numbers > Active Number, click on your phone number and, in the Voice Configuration section, paste the NGROK_URL appended with /twilio/voice as your webhook URL. Make sure it matches the provided example, then click Save Configuration.
   ```bash
   https://xxxx-xxxx-xxx-xxxx-xxxx-xxxx-xxxx-xxxx-xxxx.ngrok-free.app/twilio/voice
10. You're all set—just call the number and you're ready to go!
   
