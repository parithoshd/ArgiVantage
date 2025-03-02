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
from twilio.rest import Client
import asyncio

# Load environment variables
load_dotenv()

twilio_api_key_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_api_key_secret = os.getenv("TWILIO_API_KEY_SECRET")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Start NGROK tunnel (only if not already running)
if not os.getenv("NGROK_URL"):
    public_url = ngrok.connect(8000).public_url
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

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "FastAPI Twilio Voice Bot is running!"}

# Load and Process Multiple Documents
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

        recording_url = form_dict.get("RecordingUrl")
        response = VoiceResponse()

        if not recording_url:
            response.say("Welcome to Agrivantage! I'm here to answer your question about sustainable agriculture. Please ask your question after the beep.", voice="alice")
            response.record(
                timeout=8,
                transcribe=False,
                play_beep=True,
                finish_on_key="#",
                recording_channels="single",
                audio_format="wav",
                action=f"{ngrok_url}/twilio/voice"
            )
            return Response(content=str(response), media_type="application/xml")

        transcript = await transcribe_audio(recording_url)
        if transcript:
            response_text = get_rag_response(transcript)
            response.say(response_text, voice="alice")

            # Allow user to ask another question
            response.say("Would you like to ask another question? Press 1 to continue or any other key to end the call.", voice="alice")
            gather = response.gather(numDigits=1, action=f"{ngrok_url}/twilio/voice-loop", method="POST")
            response.append(gather)

        else:
            response.say("I didn't catch that. Please try again.", voice="alice")

        return Response(content=str(response), media_type="application/xml")

    except Exception as e:
        return Response("Internal Server Error", status_code=500)

@app.post("/twilio/voice-loop")
async def handle_voice_loop(request: Request):
    try:
        form_data = await request.form()
        digits = form_data.get("Digits")

        response = VoiceResponse()

        if digits == "1":
            response.say("Great! Please ask your next question after the beep.", voice="alice")
            response.record(
                timeout=8,
                transcribe=False,
                play_beep=True,
                finish_on_key="#",
                recording_channels="single",
                audio_format="wav",
                action=f"{ngrok_url}/twilio/voice"
            )
        else:
            response.say("Thank you for using Agrivantage. Goodbye!", voice="alice")
            response.hangup()

        return Response(content=str(response), media_type="application/xml")

    except Exception as e:
        return Response("Internal Server Error", status_code=500)

async def transcribe_audio(recording_url):
    try:
        if not recording_url:
            return ""

        auth = aiohttp.BasicAuth(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_API_KEY_SECRET"))
        max_retries = 4

        for attempt in range(max_retries):
            async with aiohttp.ClientSession() as session:
                async with session.get(recording_url, auth=auth) as audio_response:
                    if audio_response.status == 200:
                        audio_data = await audio_response.read()
                        break
                    elif attempt < max_retries - 1:
                        await asyncio.sleep(2)
                    else:
                        return ""

        if len(audio_data) < 1000:
            return ""

        form_data = aiohttp.FormData()
        form_data.add_field("file", audio_data, filename="temp_audio.wav", content_type="audio/wav")
        form_data.add_field("model", "whisper-1")

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/audio/transcriptions",
                                    headers={"Authorization": f"Bearer {openai_api_key}"},
                                    data=form_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("text", "")
                else:
                    return ""

    except Exception as e:
        return "Sorry, I encountered an error while processing your request."

def get_rag_response(query: str) -> str:
    retrieved_docs = retriever.invoke(query)

    if not retrieved_docs or len(retrieved_docs) == 0:
        return "I'm sorry, but I can only answer questions related to sustainable agriculture. Please ask a relevant question."

    context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])

    custom_prompt = (
        "You are an AI assistant specializing in sustainable agriculture. "
        "You must *only answer questions based on the following context*. "
        "If the user's question is not related to the context, respond with: "
        "'I'm sorry, but I can only answer questions related to sustainable agriculture.'\n\n"
        f"Context: {context_text}\n\n"
        f"User Query: {query}\n"
        "Answer:"
    )

    response = qa_chain.run(custom_prompt)
    return response.strip()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
