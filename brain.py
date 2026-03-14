import openai
import os
from dotenv import load_dotenv # <--- Ajoute ça
from gtts import gTTS
import threading

# Charge les variables du fichier .env
load_dotenv()

# Récupère la clé de manière sécurisée
openai.api_key = os.getenv("OPENAI_API_KEY")

def parler(texte):
    # ... le reste du code reste le même ...
