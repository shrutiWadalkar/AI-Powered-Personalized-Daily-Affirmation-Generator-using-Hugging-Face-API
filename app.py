import os
import requests
from flask import Flask, render_template, request
from gtts import gTTS
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Hugging Face API key
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Hugging Face Inference API URL (Replace with the desired model)
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"  # You can change the model
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

# Headers for API request
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# Function to generate affirmation using Hugging Face API
def generate_affirmation(mood_input):
    prompt = f"Generate a short, energetic positive affirmation for someone feeling {mood_input}. Keep it concise and uplifting."

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 30,  # Shorter response
            "temperature": 1.0,  # Increase randomness
            "top_p": 0.95,  # Reduce repetition
            "do_sample": True  # Enable sampling
            }
    }
    try:
        response = requests.post(HF_API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        affirmation = response.json()[0]["generated_text"].replace(prompt, "").strip()

        return affirmation
    except requests.exceptions.RequestException as e:
        print(f"Error calling Hugging Face API: {e}")
        return "Sorry, I couldn't generate an affirmation at the moment."

# Function to convert text to speech
import requests

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # You can change this to a voice of your choice.

def text_to_speech(affirmation):
    if not os.path.exists("static"):
        os.makedirs("static")

    filename = os.path.join("static", "affirmation.mp3")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "text": affirmation,
        "voice_settings": {
            "stability": 0.5,   # Adjust stability (lower makes it more natural)
            "similarity_boost": 0.8  # Adjust how close it sounds to real human voice
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        with open(filename, "wb") as audio_file:
            audio_file.write(response.content)
        return filename
    else:
        print("Error:", response.json())
        return "Error generating audio"

import random  # Import random module

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        mood_input = request.form["mood"]
        affirmation = generate_affirmation(mood_input)
        
        # Convert affirmation to speech
        audio_file = text_to_speech(affirmation)

        # Generate a random number and pass it to the template
        random_number = random.randint(1, 100000)

        return render_template("index.html", affirmation=affirmation, audio_file=audio_file, random_number=random_number)
    
    return render_template("index.html", affirmation=None, audio_file=None, random_number=random.randint(1, 100000))

if __name__ == "__main__":
    app.run(debug=True)
