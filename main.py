import keyboard
import time
import wave
from pydub import AudioSegment
import pyaudio
import whisper
import requests
import json

#get model
model = whisper.load_model("base")

# Define recording parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
WAVE_OUTPUT_FILENAME = "output.wav"

# Set the key we want to detect
key_to_detect = 'a'

# Set a flag to keep track of whether the key is being held down
key_held_down = False

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open recording stream
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

frames = []

def translate_text(translate):
    url = "https://libretranslate.com/translate"
    payload = {
        "q": f"{translate}",
        "source": "en",
        "target": "ja",
        "format": "text",
        "api_key": ""
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(payload), headers=headers)
    data = json.loads(response.text)
    print(data)

# Start an infinite loop to detect key presses and releases
while True:
    # Check if the key is currently being held down
    if keyboard.is_pressed(key_to_detect):
        # If it's not already being held down, set the flag to True
        data = stream.read(CHUNK)
        frames.append(data)
        if not key_held_down:
            print(f"Key '{key_to_detect}' is being held down!")
            key_held_down = True
    else:
        # If the key was being held down but is now released, reset the flag
        if key_held_down:
            time.sleep(2)
            print(f"Key '{key_to_detect}' was released!")
            print("Recording finished.")

            #Stop recording stream
            #stream.stop_stream()
            #stream.close()
            #audio.terminate()

            # Save recorded audio data to file
            waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(audio.get_sample_size(FORMAT))
            waveFile.setframerate(RATE)
            waveFile.writeframes(b''.join(frames))
            waveFile.close()
            key_held_down = False

            frames = []

            result = model.transcribe("output.wav")
            print(result["text"])
    time.sleep(0.01)