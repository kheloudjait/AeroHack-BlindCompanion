import os
import time
import threading
import queue
import json
from dotenv import load_dotenv

import pyttsx3
import vosk
import pyaudio
from openai import OpenAI

from simulator import DroneSimulator
from vision import DroneVision

class AIDroneGuide:
    def __init__(self, api_key=None):
        print("🚁 Initialisation AeroHack...")
        load_dotenv()

        # 1. AUTHENTIFICATION
        self.api_key = api_key or os.getenv("GITHUB_TOKEN") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            self.api_key = input("🔑 Clé manquante. Entre ta clé GitHub ou OpenAI : ").strip()

        if self.api_key.startswith("gh"):
            self.client = OpenAI(base_url="https://models.inference.ai.azure.com", api_key=self.api_key)
            print("✅ Mode GITHUB (Étudiant)")
        else:
            self.client = OpenAI(api_key=self.api_key)
            print("✅ Mode OPENAI")

        # 2. SYSTÈMES
        self.drone = DroneSimulator()
        self.vision = DroneVision()
        
        # Gestion de la voix via une file d'attente (évite les crashs Windows)
        self.voice_queue = queue.Queue()
        threading.Thread(target=self._worker_voix, daemon=True).start()
        
        # Reconnaissance Vocale
        if not os.path.exists("vosk-model-small-fr-0.22"):
            print("❌ DOSSIER VOSK MANQUANT ! Le dossier 'vosk-model-small-fr-0.22' doit être ici.")
        self.vosk_model = vosk.Model("vosk-model-small-fr-0.22")
        self.rec = vosk.KaldiRecognizer(self.vosk_model, 16000)
        
        self.conversation_history = [
            {"role": "system", "content": "Tu es l'IA d'un drone pour aveugles. Réponds en une phrase courte."}
        ]

    def _worker_voix(self):
        """Boucle qui attend des messages pour les lire à voix haute"""
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        while True:
            texte = self.voice_queue.get()
            if texte is None: break
            engine.say(texte)
            engine.runAndWait()
            self.voice_queue.task_done()

    def parler(self, texte):
        """Ajoute un message à la file d'attente vocale"""
        print(f"🤖 Drone: {texte}")
        self.voice_queue.put(texte)

    def ecouter(self):
        """Écoute sans s'arrêter jusqu'à entendre une phrase"""
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()
        
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if self.rec.AcceptWaveform(data):
                result = json.loads(self.rec.Result())
                phrase = result.get("text", "")
                if phrase.strip():
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                    return phrase

    def reflechir_et_repondre(self, texte_utilisateur):
        """Envoie la vision + le texte à l'IA"""
        objets, _ = self.vision.obtenir_objets()
        contexte_visuel = f"Objets détectés: {', '.join(objets)}" if objets else "Chemin libre."
        
        prompt = f"User: {texte_utilisateur}. Vision: {contexte_visuel}"
        self.conversation_history.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.conversation_history,
                temperature=0.7
            )
            answer = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": answer})
            return answer
        except Exception as e:
            return f"Problème technique : {str(e)}"

    def run(self):
        self.parler("Système activé.")
        try:
            while True:
                commande = self.ecouter()
                print(f"👤 Vous: {commande}")
                
                if any(word in commande for word in ["quitter", "stop", "éteindre"]):
                    self.parler("Fermeture du système.")
                    break
                
                reponse = self.reflechir_et_repondre(commande)
                self.parler(reponse)
                
                # Commandes drone basiques
                if "avance" in reponse.lower(): self.drone.move_forward(50)
                if "tourne" in reponse.lower(): self.drone.rotate_clockwise(90)
                    
        finally:
            self.vision.arreter()
            self.voice_queue.put(None) # Arrête le worker voix

if __name__ == "__main__":
    app = AIDroneGuide()
    app.run()
    