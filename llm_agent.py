import os
import json
import wave
import numpy as np
from groq import Groq
import whisper
from calendar_service import create_appointment

# Initialize Whisper model globally so it's only loaded once
print("Loading Whisper model...")
try:
    whisper_model = whisper.load_model("base")
except Exception as e:
    print(f"Failed to load whisper: {e}")
    whisper_model = None
print("Whisper model loaded.")

def load_wav_to_numpy(filename):
    with wave.open(filename, 'rb') as wf:
        data = wf.readframes(wf.getnframes())
    # Convert 16-bit PCM bytes to float32 between -1.0 and 1.0
    audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
    return audio_data

def transcribe_audio(file_path):
    if whisper_model is None:
        return "Whisper model not loaded."
    
    # Load audio into memory using standard libraries (bypasses ffmpeg requirement)
    audio_array = load_wav_to_numpy(file_path)
    
    result = whisper_model.transcribe(audio_array, fp16=False)
    return result["text"]

SYSTEM_PROMPT = """You are a helpful, human-like receptionist for ABC Dental Hospital.
Keep your responses concise and conversational, as they will be spoken aloud to the user via Text-to-Speech.
Your goal is to collect the user's full name and their desired appointment date and time.
If you don't have all the information, politely ask the user for the missing details.
Assume the current year is 2026.

CRITICAL INSTRUCTION:
Once the user has provided their Name, Date, and Time, you MUST output a JSON object containing exactly those details. 
The JSON must be wrapped in ```json and ``` tags.
It must contain these exact keys:
- "date_str": The date in YYYY-MM-DD format.
- "time_str": The time in 24-hour HH:MM format.
- "patient_name": The user's full name.

Example:
```json
{
  "date_str": "2026-05-27",
  "time_str": "10:00",
  "patient_name": "John Doe"
}
```
Do NOT output this JSON until you have collected all three pieces of information.
"""

class LLMAgent:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.model = "llama-3.3-70b-versatile"

    def process_message(self, user_text):
        import re
        self.messages.append({"role": "user", "content": user_text})

        # Step 1: Get normal chat response from LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            max_tokens=4096
        )

        content = response.choices[0].message.content or ""
        
        # Step 2: Check if the LLM outputted the required JSON block
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        
        if json_match:
            # The LLM has collected all info and output the JSON
            try:
                json_str = json_match.group(1)
                function_args = json.loads(json_str)
                print(f"Extracted JSON for booking: {function_args}")
                
                # Execute the booking
                function_response = create_appointment(
                    date_str=function_args.get("date_str"),
                    time_str=function_args.get("time_str"),
                    patient_name=function_args.get("patient_name")
                )
                
                # Log the exact technical response to the terminal (invisible to the user UI)
                print("========================================")
                print(f"CALENDAR API RESPONSE:\n{function_response}")
                print("========================================")
                
                # Step 3: Tell the LLM the booking result and ask it to confirm
                self.messages.append({"role": "assistant", "content": content})
                self.messages.append({"role": "system", "content": f"The booking attempt returned: {function_response}. If it failed, politely apologize to the user but do NOT mention technical details. If it succeeded, confirm it in a friendly sentence."})
                
                second_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages
                )
                
                final_text = second_response.choices[0].message.content
                self.messages.append({"role": "assistant", "content": final_text})
                
                # Strip out any residual JSON if the model hallucinates it again
                clean_text = re.sub(r'```json.*?```', '', final_text, flags=re.DOTALL)
                return clean_text.strip()
                
            except Exception as e:
                print("Failed to parse extracted JSON:", e)

        # If no JSON was found (still collecting info), just return the conversational text
        self.messages.append({"role": "assistant", "content": content})
        clean_text = re.sub(r'```json.*?```', '', content, flags=re.DOTALL)
        return clean_text.strip()
