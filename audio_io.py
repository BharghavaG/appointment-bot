import pyaudio
import wave
import time
import os
import tempfile
from gtts import gTTS
import pygame
import math
import struct

# Configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000 # Whisper prefers 16kHz
SILENCE_THRESHOLD = 500 # Adjust based on mic sensitivity
SILENCE_DURATION = 2.0 # seconds of silence before cutting

def get_rms(block):
    # Calculate RMS (Root Mean Square) manually instead of using audioop
    # 'block' is bytes of 16-bit audio
    count = len(block) // 2
    if count == 0:
        return 0
    shorts = struct.unpack("%dh" % count, block)
    sum_squares = sum(s**2 for s in shorts)
    return math.sqrt(sum_squares / count)

def record_audio_until_silence(output_filename="temp_audio.wav"):
    """
    Records audio from the microphone until silence is detected.
    Returns the filename of the recorded audio, or None if no speech was detected.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Listening...")
    frames = []
    has_spoken = False
    silence_start_time = None

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            rms = get_rms(data) # Get volume of chunk

            if rms > SILENCE_THRESHOLD:
                if not has_spoken:
                    print("Speech detected. Recording...")
                    has_spoken = True
                silence_start_time = None # Reset silence timer
            elif has_spoken:
                if silence_start_time is None:
                    silence_start_time = time.time()
                elif time.time() - silence_start_time > SILENCE_DURATION:
                    print("Silence detected. Stopping recording.")
                    break
            
            if has_spoken:
                frames.append(data)
    
    except KeyboardInterrupt:
        print("Recording interrupted.")
    
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    if not has_spoken:
        return None

    # Save to file
    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return output_filename

def play_audio_from_text(text):
    """
    Converts text to speech and plays it immediately.
    """
    if not text.strip():
        return

    print(f"Bot speaking: {text}")
    
    # Generate TTS
    tts = gTTS(text=text, lang='en')
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    temp_file.close()

    # Play using pygame
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file.name)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    finally:
        # Cleanup
        pygame.mixer.quit()
        try:
            os.remove(temp_file.name)
        except OSError:
            pass

if __name__ == "__main__":
    # Test script
    print("Testing audio IO...")
    play_audio_from_text("Hello, this is a test of the audio playback system.")
    filename = record_audio_until_silence()
    if filename:
        print(f"Recorded to {filename}")
        play_audio_from_text("I heard you say something. The test was successful.")
