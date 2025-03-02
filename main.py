from fastapi import FastAPI, Request
import openai
import requests
import os
from dotenv import load_dotenv
from deepgram import DeepgramClient
from twilio.twiml.voice_response import VoiceResponse
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import aiohttp
import json
from pyngrok import ngrok
from fastapi.responses import Response

import asyncio

from twilio.rest import Client


# Load environment variables
load_dotenv()

twilio_api_key_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_api_key_secret = os.getenv("TWILIO_API_KEY_SECRET")

openai_api_key = os.getenv("OPENAI_API_KEY")

if not os.getenv("NGROK_URL"):
    public_url = ngrok.connect(8000).public_url
    print(f"NGROK URL: {public_url}")
    
    env_file_path = ".env"
    if os.path.exists(env_file_path):
        with open(env_file_path, "r") as env_file:
            lines = env_file.readlines()
        
        new_lines = [line for line in lines if not line.startswith("NGROK_URL=")]
        new_lines.append(f"NGROK_URL={public_url}\n")
        
        with open(env_file_path, "w") as env_file:
            env_file.writelines(new_lines)
    else:
        with open(env_file_path, "w") as env_file:
            env_file.write(f"NGROK_URL={public_url}\n")

load_dotenv()
ngrok_url = os.getenv("NGROK_URL")

print(f"NGROK URL loaded from .env: {ngrok_url}")

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "FastAPI Twilio Voice Bot is running!"}

text_loader = DirectoryLoader("documents", glob="*.txt")
pdf_loader = DirectoryLoader("documents", glob="*.pdf", loader_cls=PyMuPDFLoader)

text_docs = text_loader.load()
pdf_docs = pdf_loader.load()
all_docs = text_docs + pdf_docs

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
texts = text_splitter.split_documents(all_docs)

vectorstore = FAISS.from_documents(texts, OpenAIEmbeddings(openai_api_key=openai_api_key))
retriever = vectorstore.as_retriever()
qa_chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(openai_api_key=openai_api_key), retriever=retriever)

@app.post("/twilio/voice")
async def handle_voice_call(request: Request):
    try:
        form_data = await request.form()
        form_dict = dict(form_data)
        print("Received Twilio Webhook Data:", json.dumps(form_dict, indent=2))

        recording_url = form_dict.get("RecordingUrl")
        response = VoiceResponse()

        print(f"Recording URL: {recording_url}")

        if not recording_url:
            response.say("Hello! Please ask your question about agriculture.", voice="alice")
            response.record(
            timeout=8,
            transcribe=False,  
            play_beep=True,  
            finish_on_key="#",
            recording_channels="single",
            audio_format="mp3",
            action=f"{ngrok_url}/twilio/voice"
            )
            return Response(content=str(response), media_type="application/xml")

        transcript = await transcribe_audio(recording_url)
        if transcript:
            response_text = get_rag_response(transcript)
            response.say(response_text, voice="alice")
        else:
            response.say("I didn't catch that. Please try again.", voice="alice")

        return Response(content=str(response), media_type="application/xml")

    except Exception as e:
        print(f"Error in /twilio/voice: {e}")
        return Response("Internal Server Error", status_code=500)



twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_auth_token = os.getenv("TWILIO_API_KEY_SECRET")
openai_api_key = os.getenv("OPENAI_API_KEY")

async def transcribe_audio(recording_url):
    try:
        if not recording_url:
            print("No recording URL received from Twilio!")
            return ""

        print(f"Attempting to download recording from: {recording_url}")

        auth = aiohttp.BasicAuth(twilio_sid, twilio_auth_token)
        
        max_retries = 5
        for attempt in range(max_retries):
            async with aiohttp.ClientSession() as session:
                async with session.get(recording_url, auth=auth) as audio_response:
                    if audio_response.status == 200:
                        audio_data = await audio_response.read()
                        break
                    elif attempt < max_retries - 1:
                        print(f"Twilio recording not available yet. Retrying... ({attempt+1}/{max_retries})")
                        await asyncio.sleep(2)
                    else:
                        print(f"Failed to download recording: HTTP {audio_response.status}")
                        return ""

        print(f"Audio file downloaded. Size: {len(audio_data)} bytes")

        if len(audio_data) < 1000:
            print("The recording is empty or too short.")
            return ""

        with open("test_audio.wav", "wb") as f:
            f.write(audio_data)

        print("Audio file saved as 'test_audio.wav'. Try playing it manually.")

        form_data = aiohttp.FormData()
        form_data.add_field("file", audio_data, filename="temp_audio.wav", content_type="audio/wav")
        form_data.add_field("model", "whisper-1")

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/audio/transcriptions",
                                    headers={"Authorization": f"Bearer {openai_api_key}"},
                                    data=form_data) as response:
                if response.status == 200:
                    result = await response.json()
                    transcript = result.get("text", "")
                    print(f"Transcription: {transcript}")
                    return transcript
                else:
                    print(f"Failed to transcribe audio. Status code: {response.status}")
                    return ""

    except Exception as e:
        print(f"OpenAI Whisper STT Error: {e}")
        return "Sorry, I encountered an error while processing your request."

def get_rag_response(query: str) -> str:
    response = qa_chain.run(query)
    return response.strip()

if _name_ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)