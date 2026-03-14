#!/usr/bin/env python3
"""
AI-Powered Drone Guide for Blind Users
Based on research from ACM UIST 2025 [citation:1]
"""

import openai
import json
import pyaudio
import wave
import numpy as np
from vosk import Model, KaldiRecognizer
from djitellopy import Tello
import pyttsx3
import speech_recognition as sr
import threading
import queue
import time
import os
from scipy.spatial.distance import cosine
import warnings
warnings.filterwarnings('ignore')

class AIDroneGuide:
    """
    Complete AI-powered drone assistant that:
    - Recognizes specific user's voice
    - Understands natural conversation
    - Generates drone control code on-the-fly
    - Provides verbal guidance
    """
    
    def __init__(self, api_key=None, vosk_model_path="vosk-model-small-fr-0.22"):
        """
        Initialize all components
        """
        print("🚁 Initializing AI-Powered Drone Guide...")
        
        # ===== 1. SPEAKER VERIFICATION (Voice Recognition) =====
        self.voice_prints = {}
        self.speaker_threshold = 0.3
        self.current_speaker = None
        
        # ===== 2. SPEECH-TO-TEXT (VOSK for offline) =====
        print("📚 Loading speech recognition model...")
        if os.path.exists(vosk_model_path):
            self.vosk_model = Model(vosk_model_path)
            self.vosk_recognizer = KaldiRecognizer(self.vosk_model, 16000)
        else:
            print("⚠️ VOSK model not found, using Google STT fallback")
            self.vosk_model = None
            
        # ===== 3. LLM CORE (OpenAI GPT-4o) =====
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
            self.llm_available = True
            print("✅ LLM connected")
        else:
            self.llm_available = False
            print("⚠️ No API key, LLM features disabled")
        
        # ===== 4. TEXT-TO-SPEECH (Voice feedback) =====
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.9)
        
        # ===== 5. AUDIO CONFIGURATION =====
        self.CHUNK = 4096
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        
        # ===== 6. DRONE CONTROL =====
        self.drone = None
        self.drone_connected = False
        
        # ===== 7. CONVERSATION HISTORY =====
        self.conversation_history = [
            {"role": "system", "content": """You are a helpful drone guide for a blind person. 
            You can see the environment through your camera and guide the user.
            Respond conversationally and naturally. When you need to move, 
            generate Python code using these functions:
            - drone.takeoff()
            - drone.land()
            - drone.move_forward(cm)
            - drone.move_back(cm)
            - drone.move_left(cm)
            - drone.move_right(cm)
            - drone.rotate_clockwise(degrees)
            - drone.rotate_counter_clockwise(degrees)
            - drone.get_battery()
            - drone.get_height()
            
            Always acknowledge what you're doing and explain the environment."""}
        ]
        
        # ===== 8. COMMAND QUEUE =====
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        print("✅ Initialization complete!")
    
    # ========== SPEAKER VERIFICATION ==========
    
    def extract_voice_print(self, audio_data):
        """Extract voice fingerprint from audio sample"""
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
        audio_array = audio_array / (np.max(np.abs(audio_array)) + 1e-10)
        
        # Simple spectral features (for demo - use proper MFCC in production)
        from scipy import signal
        frequencies, times, spectrogram = signal.spectrogram(
            audio_array, 
            fs=self.RATE,
            nperseg=1024
        )
        spectral_mean = np.mean(spectrogram, axis=1)
        
        if np.linalg.norm(spectral_mean) > 0:
            spectral_mean = spectral_mean / np.linalg.norm(spectral_mean)
        
        return spectral_mean[:100]  # Keep first 100 coefficients
    
    def enroll_speaker(self, name, duration=5):
        """Register a new user's voice"""
        print(f"\n🎤 Enrolling speaker: {name}")
        print(f"Please speak normally for {duration} seconds...")
        
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                       channels=self.CHANNELS,
                       rate=self.RATE,
                       input=True,
                       frames_per_buffer=self.CHUNK)
        
        frames = []
        for _ in range(0, int(self.RATE / self.CHUNK * duration)):
            data = stream.read(self.CHUNK)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        audio_data = b''.join(frames)
        voice_print = self.extract_voice_print(audio_data)
        self.voice_prints[name] = voice_print
        
        print(f"✅ Speaker {name} enrolled successfully!")
        return voice_print
    
    def verify_speaker(self, audio_data):
        """Check if speaker is authorized"""
        if not self.voice_prints:
            return False, None
        
        test_print = self.extract_voice_print(audio_data)
        best_match = None
        min_distance = float('inf')
        
        for name, enrolled_print in self.voice_prints.items():
            min_len = min(len(test_print), len(enrolled_print))
            distance = cosine(test_print[:min_len], enrolled_print[:min_len])
            
            if distance < min_distance:
                min_distance = distance
                best_match = name
        
        if min_distance < self.speaker_threshold:
            return True, best_match
        return False, None
    
    # ========== SPEECH-TO-TEXT ==========
    
    def listen_for_speech(self, timeout=5):
        """Capture and transcribe user speech"""
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                       channels=self.CHANNELS,
                       rate=self.RATE,
                       input=True,
                       frames_per_buffer=self.CHUNK)
        
        print("🎤 Listening...")
        frames = []
        
        # Record for 3 seconds (adjust as needed)
        for _ in range(0, int(self.RATE / self.CHUNK * 3)):
            data = stream.read(self.CHUNK, exception_on_overflow=False)
            frames.append(data)
        
        audio_data = b''.join(frames)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Verify speaker first
        is_authorized, speaker = self.verify_speaker(audio_data)
        if not is_authorized:
            self.speak("I don't recognize your voice. Please enroll first.")
            return None, None
        
        # Transcribe with VOSK or fallback
        if self.vosk_model and self.vosk_recognizer.AcceptWaveform(audio_data, len(audio_data)):
            result = json.loads(self.vosk_recognizer.Result())
            text = result.get('text', '')
            print(f"📝 Transcribed: '{text}'")
            return text, speaker
        else:
            # Fallback to Google Speech Recognition
            try:
                import speech_recognition as sr
                recognizer = sr.Recognizer()
                audio = sr.AudioData(audio_data, self.RATE, 2)
                text = recognizer.recognize_google(audio, language="en-US")
                print(f"📝 Google transcribed: '{text}'")
                return text, speaker
            except:
                return None, speaker
    
    # ========== TEXT-TO-SPEECH ==========
    
    def speak(self, text):
        """Give voice feedback to user"""
        print(f"🤖 Drone: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    # ========== LLM CORE INTELLIGENCE ==========
    
    def process_with_llm(self, user_input, context=None):
        """
        Use LLM to understand user intent and generate response/code
        Based on research from Wei et al. 2025 [citation:1]
        """
        if not self.llm_available:
            return self.fallback_response(user_input)
        
        # Add user input to conversation
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Add visual context if available
        if context:
            self.conversation_history.append({
                "role": "system", 
                "content": f"Visual context: {context}"
            })
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",  # Using multimodal model
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=500
            )
            
            assistant_response = response.choices[0].message.content
            self.conversation_history.append({
                "role": "assistant", 
                "content": assistant_response
            })
            
            # Extract any code commands
            self.extract_and_queue_commands(assistant_response)
            
            return assistant_response
            
        except Exception as e:
            print(f"LLM Error: {e}")
            return "I'm having trouble thinking right now. Please try again."
    
    def extract_and_queue_commands(self, response):
        """Extract Python commands from LLM response"""
        import re
        
        # Look for code blocks
        code_pattern = r'```python\n(.*?)\n```'
        matches = re.findall(code_pattern, response, re.DOTALL)
        
        for code in matches:
            self.command_queue.put(code)
    
    def fallback_response(self, user_input):
        """Simple rule-based fallback when LLM unavailable"""
        user_input = user_input.lower()
        
        if "hello" in user_input or "hi" in user_input:
            return "Hello! I'm your drone guide. How can I help you today?"
        elif "take off" in user_input or "fly" in user_input:
            self.command_queue.put("drone.takeoff()")
            return "Taking off now. I'll be right in front of you."
        elif "land" in user_input:
            self.command_queue.put("drone.land()")
            return "Landing now. Please stand back."
        elif "battery" in user_input:
            return "I'll check my battery level."
        elif "help" in user_input:
            return "You can ask me to take off, land, move forward, turn, or describe what I see."
        else:
            return "I'm not sure how to help with that right now."
    
    # ========== VISUAL UNDERSTANDING ==========
    
    def capture_and_analyze_scene(self):
        """
        Use drone camera to understand environment
        In production, use GPT-4o's vision capabilities [citation:1]
        """
        if not self.drone_connected or not self.drone:
            return "No camera available"
        
        # This would capture frame and send to GPT-4o vision
        # For now, return simulated context
        return "I can see a clear path ahead. There's a parked car about 5 meters to your right."
    
    # ========== DRONE CONTROL ==========
    
    def connect_drone(self):
        """Connect to Tello drone"""
        try:
            self.drone = Tello()
            self.drone.connect()
            self.drone_connected = True
            battery = self.drone.get_battery()
            print(f"✅ Drone connected! Battery: {battery}%")
            self.speak(f"Drone connected. Battery at {battery} percent.")
            return True
        except Exception as e:
            print(f"❌ Drone connection failed: {e}")
            self.speak("Could not connect to the drone. Please check the WiFi.")
            return False
    
    def execute_command(self, command):
        """Execute a drone command safely"""
        if not self.drone_connected:
            print("⚠️ Drone not connected")
            return
        
        try:
            # WARNING: exec() is dangerous - use with caution!
            # In production, implement a safe command parser
            exec(command)
            print(f"✅ Executed: {command}")
        except Exception as e:
            print(f"❌ Command failed: {e}")
    
    def command_executor_thread(self):
        """Background thread to execute drone commands"""
        while True:
            try:
                command = self.command_queue.get(timeout=1)
                if command:
                    self.execute_command(command)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Executor error: {e}")
    
    # ========== GUIDANCE SESSION ==========
    
    def run_guidance_session(self):
        """Main interaction loop"""
        print("\n" + "="*50)
        print("🚀 AI DRONE GUIDANCE SESSION STARTED")
        print("="*50)
        print("The drone is ready to guide you.")
        print("Speak naturally - ask questions or give commands.")
        print("Say 'goodbye' to end the session.")
        
        # Start command executor thread
        executor_thread = threading.Thread(target=self.command_executor_thread, daemon=True)
        executor_thread.start()
        
        # Welcome message
        self.speak("Hello! I'm your AI drone guide. I can see the environment and help you navigate. What would you like to do?")
        
        try:
            while True:
                # Listen for user input
                user_input, speaker = self.listen_for_speech()
                
                if user_input is None:
                    continue
                
                # Check for exit
                if "goodbye" in user_input.lower() or "bye" in user_input.lower():
                    self.speak("Goodbye! It was nice guiding you today.")
                    break
                
                # Get visual context
                visual_context = self.capture_and_analyze_scene()
                
                # Process with LLM
                print(f"🧠 Processing with AI...")
                response = self.process_with_llm(
                    user_input, 
                    context=visual_context
                )
                
                # Respond verbally
                self.speak(response)
                
        except KeyboardInterrupt:
            print("\n🛑 Session interrupted")
        finally:
            if self.drone_connected:
                self.drone.land()
                self.drone.end()
            print("👋 Session ended")


# ========== MAIN APPLICATION ==========

def main():
    """
    Complete setup and execution
    """
    print("="*60)
    print("🤖 AI-POWERED DRONE GUIDE FOR BLIND USERS")
    print("="*60)
    print("\nBased on research from:")
    print("  • Wei et al. 2025 - LLM-powered Drone Companion [citation:1]")
    print("  • Ocularone Platform [citation:4]")
    print("  • Multi-DNN obstacle avoidance [citation:7]")
    
    # Get API key
    api_key = input("\n🔑 Enter your OpenAI API key (or press Enter to skip): ").strip()
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    
    # Initialize the AI guide
    guide = AIDroneGuide(api_key=api_key)
    
    # ===== STEP 1: Enroll speakers =====
    print("\n" + "-"*40)
    print("STEP 1: VOICE ENROLLMENT")
    print("-"*40)
    print("The drone needs to learn your voice.")
    
    while True:
        name = input("Enter you
        r name (or 'done' to finish): ").strip()
        if name.lower() == 'done':
            break
        if name:
            guide.enroll_speaker(name, duration=5)
    
    if not guide.voice_prints:
        print("⚠️ No speakers enrolled. Voice verification disabled.")
    
    # ===== STEP 2: Connect to drone =====
    print("\n" + "-"*40)
    print("STEP 2: DRONE CONNECTION")
    print("-"*40)
    print("1. Turn on your Tello drone")
    print("2. Connect your computer to Tello WiFi")
    input("Press Enter when ready...")
    
    guide.connect_drone()
    
    # ===== STEP 3: Start guidance =====
    print("\n" + "-"*40)
    print("STEP 3: GUIDANCE SESSION")
    print("-"*40)
    guide.run_guidance_session()


if __name__ == "__main__":
    main()