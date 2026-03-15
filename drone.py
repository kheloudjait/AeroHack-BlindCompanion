import os
import pygame
import threading
import pyttsx3
import random
import tempfile
import time

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

class Drone:
    def __init__(self):
        self.x = 400
        self.y = 300
        self.radius = 12
        self.sensor_range = 50 # How far the drone "sees"
        self.speed = 5
        self.flying = False
        self.alert = False

        # Initialize TTS engine (pyttsx3). Use sapi5 on Windows when available.
        try:
            self.engine = pyttsx3.init(driverName="sapi5")
        except Exception:
            self.engine = pyttsx3.init()

        # Ensure the voice engine uses a sane volume and voice
        try:
            self.engine.setProperty("volume", 1.0)  # max volume
            self.engine.setProperty("rate", 150)
            voices = self.engine.getProperty("voices")
            if voices:
                self.engine.setProperty("voice", voices[0].id)
        except Exception:
            pass

        self._speech_lock = threading.Lock()
        self._speaking = False
        self.message = ""
        self.message_until = 0

        # Track whether pygame mixer was initialized for gTTS fallback
        self._mixer_initialized = False
        self._use_gtts = gTTS is not None

    def speak(self, text, duration=4):
        # Avoid interrupting a currently-playing voice response
        if getattr(self, '_speaking', False):
            return

        print(f"Drone says: {text}")
        self.message = text
        self.message_until = time.time() + duration
        threading.Thread(target=self._say, args=(text,), daemon=True).start()

    def clear_message_if_needed(self):
        if self.message and time.time() > self.message_until:
            self.message = ""

    def _say(self, text):
        with self._speech_lock:
            self._speaking = True

            # Prefer gTTS (often more reliable across systems); fall back to pyttsx3
            if self._use_gtts:
                try:
                    print("Using gTTS for speech output")
                    self._say_with_gtts(text)
                    self._speaking = False
                    return
                except Exception as g:
                    print(f"gTTS error: {g}")

            # Fall back to pyttsx3
            try:
                print(f"pyttsx3 speaking ({len(text)} chars)")
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"TTS error (pyttsx3): {e}")

            self._speaking = False

    def _say_with_gtts(self, text):
        """Fallback TTS using gTTS + pygame mixer."""
        # Create a temporary mp3 file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            filename = tmp.name
        try:
            tts = gTTS(text=text, lang="en")
            tts.save(filename)

            # Initialize mixer once
            if not self._mixer_initialized:
                pygame.mixer.init()
                self._mixer_initialized = True

            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            print("gTTS playback started")

            # Wait until playback finishes (so speech is audible before function returns)
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            print("gTTS playback finished")
        finally:
            try:
                os.unlink(filename)
            except Exception:
                pass

    def takeoff(self):
        self.flying = True
        self.speak("Engines active. I am ready to guide you.")

    def land(self):
        self.flying = False
        self.speak("Landing now. Please watch your step.")

    # Movement with collision blocking
    def move(self, dx, dy, obstacles):
        if not self.flying:
            return False

        # If no movement is requested, do nothing (avoids spamming alerts)
        if dx == 0 and dy == 0:
            return False

        # Predicted next position
        next_x = self.x + (dx * self.speed)
        next_y = self.y + (dy * self.speed)

        # Check if next position hits an obstacle
        collision = False
        for obs in obstacles:
            rect = obs["rect"] if isinstance(obs, dict) else obs
            if rect.collidepoint(next_x, next_y):
                collision = True
                break
        
        if not collision:
            self.x = next_x
            self.y = next_y
            self.alert = False
            return True
        else:
            # Only print the warning once per blocked state to avoid spam
            if not self.alert:
                print("Alert: Obstacle detected. Path blocked!")
            self.alert = True # Trigger "Warning" state
            return False

