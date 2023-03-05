import keyboard
import time
import wave
from pydub import AudioSegment
import pyaudio
import whisper
import requests
import json
from libretranslatepy import LibreTranslateAPI
from urllib.parse import urlencode
from pygame import mixer

voicevox_url = "http://localhost:50021"

#Get Translator
lt = LibreTranslateAPI("https://translate.argosopentech.com/")

#get model
model = whisper.load_model("base.en", device= "cuda")

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
                    frames_per_buffer=CHUNK, input_device_index=2)

frames = []


def output_speak(strWaifupath):
    mixer.init(devicename = 'CABLE Input (VB-Audio Virtual Cable)') # Initialize it with the correct device
    mixer.music.load(strWaifupath) # Load the mp3
    mixer.music.play() # Play it

    while mixer.music.get_busy():  # wait for music to finish playing
        time.sleep(0.3)

    mixer.quit()
    

def speak(text_to_speech):
    speaker_id = '22' #22 ASMR , 3 Girl, 34 Cowok, 35 Nangis, 40 Laki Chad
    params_encoded = urlencode(
        {
        'text' : text_to_speech,
        'speaker' : speaker_id
        }
    )

    r = requests.post(f'{voicevox_url}/audio_query?{params_encoded}')
    voicevox_query = r.json()
    voicevox_query['volumeScale'] = 3.0
    voicevox_query['intonationScale'] = 1.0
    voicevox_query['prePhonemeLength'] = 1.0
    voicevox_query['postPhonemeLength'] = 1.0

    params_encoded = urlencode(
        {
        'speaker' : speaker_id
        }
    )

    r = requests.post(f'{voicevox_url}/synthesis?{params_encoded}', json=voicevox_query)

    with open("Waifu.wav", 'wb') as outfile:
        outfile.write(r.content)


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

            #print to jp
            strJapanText = lt.translate(result["text"], "en", "ja")
            print(strJapanText)

            #Text to speech
            print("Convert to Waifu...")
            speak(strJapanText)

            #microphone output
            print("Play to microphone...")
            output_speak("Waifu.wav")
            print("Done...")



    time.sleep(0.01)