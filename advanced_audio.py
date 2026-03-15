import speech_recognition as sr
import time

class VoiceListener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        print("Calibrating microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        print("Ready!")
    
    def listen(self, timeout=3):
        """Listen for a command and return text"""
        try:
            with self.microphone as source:
                print("\n🎤 Listening...")
                audio = self.recognizer.listen(source, timeout=timeout)
            
            print("🔄 Recognizing...")
            command = self.recognizer.recognize_google(audio)
            print(f"✅ You said: {command}")
            return command.lower()
            
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            print("❌ Could not understand")
            return ""
        except sr.RequestError:
            print("❌ Speech service error")
            return ""

# Easy-to-use function
def listen():
    listener = VoiceListener()
    return listener.listen()