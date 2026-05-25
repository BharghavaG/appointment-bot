# 🦷 AI Voice-Based Dentist Appointment Bot

A fully voice-interactive, local AI receptionist built with Python and Streamlit. This application allows users to speak directly to an AI assistant to book a dental appointment, and it automatically schedules the event on a Google Calendar.

## ✨ Features

- **🗣️ Voice-to-Text**: Listens to the user's voice using the computer's microphone and transcribes it locally using OpenAI's **Whisper** model (optimized to run on CPU without requiring `ffmpeg`).
- **🧠 Advanced LLM Brain**: Uses **Groq's Llama-3.3-70b-versatile** model to hold natural, human-like conversations and extract booking details (Name, Date, Time) using a highly stable Prompt-Engineered JSON extraction pattern.
- **🔊 Text-to-Speech**: Converts the AI's responses back into spoken audio using **Google TTS (gTTS)**.
- **📅 Google Calendar Integration**: Automatically authenticates via OAuth 2.0 and schedules the appointment directly onto the user's Google Calendar.
- **💻 Local Web UI**: Provides a clean, modern chat interface built with **Streamlit**.

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.8+**
- A Google Cloud account with the **Google Calendar API** enabled.
- A **Groq API Key** (for Llama 3 access).

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/appointment-bot.git
   cd appointment-bot
   ```

2. **Set up a virtual environment (Recommended)**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Google Calendar OAuth Setup**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project and enable the **Google Calendar API**.
   - Navigate to **APIs & Services > OAuth consent screen** and set it up (add your email as a Test User).
   - Navigate to **Credentials**, click **Create Credentials > OAuth client ID**, and choose **Desktop App**.
   - Download the JSON file and rename it to `credentials.json`. Place it in the root directory of this project.

## 🎮 Usage

Run the Streamlit application:

```bash
streamlit run app.py
```

1. Click **"Log in to Google Calendar"** on the sidebar.
2. A browser window will open. Select your Google account and **CRITICALLY: check the box granting permission to view and edit events on your calendar**.
3. Click **"Start Voice Assistant"** to begin talking to the bot!

## 🏗️ Architecture Note: JSON Extraction Pattern

This bot bypasses native LLM "tool-calling" API features, which can sometimes be unstable or hallucinate XML tags on open-weight models. Instead, it uses a robust **Structured JSON Extraction Pattern**. The LLM is prompted to converse naturally until it has all the necessary information, at which point it outputs a rigid Markdown JSON block. The Python backend intercepts this JSON, executes the calendar booking, and asks the LLM to generate a natural confirmation message.

## 📄 License

This project is licensed under the MIT License.
