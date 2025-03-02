# Contributing to Agrivantage Voice AI Assistant 🌱📞

Thank you for your interest in contributing to **Agrivantage**, an AI-powered voice system for answering agricultural queries via Twilio! 🚀 Your contributions are valuable in making this project better.

---

## 📌 Prerequisites

Before you start, make sure you have the following installed:

- [Git](https://git-scm.com/downloads)
- [Python 3.9+](https://www.python.org/downloads/)
- [Node.js & npm](https://nodejs.org/en/download/)
- [ngrok](https://ngrok.com/download)
- [Twilio Account](https://www.twilio.com/try-twilio)
- [OpenAI API Key](https://platform.openai.com/signup/)
- [A GitHub account](https://github.com/)

---

## 💡 How to Contribute

### 1️⃣ Fork and Clone the Repository

1. Click the **Fork** button on the top right of this repository.
2. Clone your forked repository to your local machine:
   ```sh
   git clone https://github.com/YOUR_GITHUB_USERNAME/Agrivantage-Voice-AI.git
   cd Agrivantage-Voice-AI
3. Add the original repository as an upstream remote:
   ```sh
   git remote add upstream https://github.com/ORIGINAL_OWNER/Agrivantage-Voice-AI.git
### 2️⃣ Set Up Your Development Environment
1. Create a .env file in the root directory.
2. Add the following variables and update them with your actual API keys:
   ```sh
   OPENAI_API_KEY=your_openai_api_key
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_API_KEY_SECRET=your_twilio_auth_token
### 4️⃣ Run the Application
1. Start the FastAPI Server
2. Expose the Server with ngrok
3. Copy the ngrok URL and update your .env file:
4. Configure Twilio Webhook
5. i.   Go to Twilio Console
   ii.  Navigate to Phone Numbers → Active Numbers.
   iii. Under Voice Configuration, paste the ngrok URL followed by /twilio/voice.
   ```sh
   https://your-ngrok-url.ngrok-free.app/twilio/voice
6. Click Save
### 5️⃣ Submitting a Contribution
📌 Creating a New Branch
Before making any changes, create a new branch:
   ```sh
   git checkout -b feature/your-feature-name
