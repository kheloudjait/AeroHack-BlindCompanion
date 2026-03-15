import pyttsx3
import random
import time

class AIResponse:
    def __init__(self):
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume
        
        # Conversation memory
        self.last_command = ""
        self.conversation_history = []
        
    def speak(self, text):
        """Make the drone speak"""
        print(f"🤖 Drone: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
        
    def process_command(self, command):
        """Understand command and generate response"""
        
        # Store in history
        self.conversation_history.append(command)
        self.last_command = command
        
        # Takeoff responses
        if "take off" in command or "takeoff" in command:
            responses = [
                "Taking off now. I'll be right in front of you.",
                "Lifting off! I can see the area clearly.",
                "Taking off. Please stand back."
            ]
            return random.choice(responses)
        
        # Landing responses
        elif "land" in command:
            responses = [
                "Landing now. Watch above.",
                "Coming down slowly.",
                "Descending to ground level."
            ]
            return random.choice(responses)
        
        # Movement responses
        elif "forward" in command:
            responses = [
                "Moving forward. Path looks clear.",
                "Advancing slowly.",
                "Going straight ahead."
            ]
            return random.choice(responses)
            
        elif "back" in command:
            responses = [
                "Moving backward.",
                "Reversing carefully."
            ]
            return random.choice(responses)
            
        elif "left" in command:
            responses = [
                "Turning left.",
                "Moving to the left side."
            ]
            return random.choice(responses)
            
        elif "right" in command:
            responses = [
                "Turning right.",
                "Moving to the right side."
            ]
            return random.choice(responses)
        
        # Help responses
        elif "help" in command:
            return "You can say: take off, land, forward, back, left, right, or where am I"
        
        # Position awareness (NEW!)
        elif "where" in command or "position" in command:
            return self.describe_position()
            
        # Battery check
        elif "battery" in command:
            return self.check_battery()
        
        # Greetings
        elif "hello" in command or "hi" in command:
            responses = [
                "Hello! I'm your drone guide. How can I help?",
                "Hi there! Ready to assist you.",
                "Hello! Say 'help' for commands."
            ]
            return random.choice(responses)
        
        # Default response
        else:
            responses = [
                "I didn't understand that. Can you repeat?",
                "Sorry, I don't know that command.",
                "Try saying 'help' for instructions."
            ]
            return random.choice(responses)
    
    def describe_position(self):
        """Simulate position awareness"""
        positions = [
            "You are 2 meters behind me. There's a clear path ahead.",
            "I'm hovering at 1.2 meters. You're safely behind me.",
            "We're in the main area. I can see walls 3 meters on each side.",
            "I estimate we've moved 5 meters from our starting point."
        ]
        return random.choice(positions)
    
    def check_battery(self):
        """Simulate battery check"""
        battery = random.randint(60, 95)
        return f"Battery at {battery}%. I can fly for about {battery//10} more minutes."
    
    def confirm_obstacle(self):
        """Called when obstacle detected"""
        responses = [
            "⚠️ Warning! Obstacle detected ahead. Stopping.",
            "⚠️ I see something in our path. Please wait.",
            "⚠️ Obstacle! Moving slightly to avoid it."
        ]
        return random.choice(responses)