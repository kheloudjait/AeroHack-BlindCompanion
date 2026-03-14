#!/usr/bin/env python3
"""
AeroGuide Pitch Simulation
For AERo-pitch Challenge - Drone Startup Competition
Simulates AI-powered drone guide for blind users without actual hardware
"""  

import time
import random
import sys

class AeroGuidePitchSimulation:
    """
    Complete simulation for pitch presentation
    Shows all features without needing a real drone
    """
    
    def __init__(self):
        self.user_name = None
        self.current_location = "Entrance Hall"
        self.destinations = {
            "bathroom": {
                "distance": 12,  # meters
                "direction": "straight ahead then right",
                "obstacles": ["chair at 5m", "slight step at 8m"]
            },
            "exit": {
                "distance": 25.,
                "direction": "straight behind you",
                "obstacles": []
            },
            "elevator": {
                "distance": 8,
                "direction": "left",
                "obstacles": ["table at 3m"]
            },
            "meeting room": {
                "distance": 15,
                "direction": "right then straight",
                "obstacles": ["open door at 7m", "person walking"]
            }
        }
        
        # Track drone's position awareness
        self.position = {
            "x": 0, "y": 0, "z": 1.2,  # meters
            "floor_tiles_passed": 0,
            "distance_to_left_wall": 2.5,
            "distance_to_right_wall": 3.1,
            "distance_behind_to_user": 2.0
        }
        
        self.battery = 87
        self.path_history = []
        
    def print_slow(self, text, delay=0.03):
        """Print text with typing effect for dramatic presentation"""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()
    
    def print_drone(self, text):
        """Print drone dialogue with blue color and prefix"""
        print(f"\033[94m🤖 Drone: {text}\033[0m")
        time.sleep(1)
    
    def print_user(self, text):
        """Print user dialogue with purple color"""
        print(f"\033[95m👤 You: {text}\033[0m")
        time.sleep(1)
    
    def print_system(self, text):
        """Print system messages with green color"""
        print(f"\033[92m🔧 {text}\033[0m")
        time.sleep(0.5)
    
    def print_alert(self, text):
        """Print alerts with yellow color"""
        print(f"\033[93m⚠️ {text}\033[0m")
        time.sleep(1)
    
    def show_position_awareness(self):
        """Demonstrate how drone knows its position"""
        self.print_system("\n📍 POSITION AWARENESS SYSTEM ACTIVE")
        time.sleep(1)
        
        print("\n┌──────────────────────────────────────────────┐")
        print("│           POSITION TRACKING DATA              │")
        print("├──────────────────────────────────────────────┤")
        print(f"│  📍 Current Position: ({self.position['x']}m, {self.position['y']}m)      │")
        print(f"│  📏 Altitude: {self.position['z']}m                          │")
        print(f"│  🧱 Distance to Left Wall: {self.position['distance_to_left_wall']}m             │")
        print(f"│  🧱 Distance to Right Wall: {self.position['distance_to_right_wall']}m            │")
        print(f"│  👤 Distance Behind to User: {self.position['distance_behind_to_user']}m           │")
        print(f"│  🔢 Floor Tiles Passed: {self.position['floor_tiles_passed']}                    │")
        print("└──────────────────────────────────────────────┘")
        time.sleep(2)
        
        self.print_drone("I'm tracking our position using multiple sensors:")
        self.print_drone("• Downward camera tracks floor patterns like a computer mouse")
        self.print_drone("• TOF sensors measure distance to walls and ceiling")
        self.print_drone("• Directional microphones locate your voice")
        self.print_drone("• Combined accuracy: ±10cm")
    
    def enroll_demo(self):
        """Demonstrate voice enrollment"""
        print("\n" + "="*60)
        print("📝 STEP 1: VOICE ENROLLMENT")
        print("="*60)
        time.sleep(1)
        
        self.print_system("This is a one-time setup - the drone learns YOUR voice")
        time.sleep(1)
        
        self.print_user("Alex (speaking for 5 seconds)...")
        self.print_system("🔴 Recording voice sample...")
        time.sleep(3)
        
        self.user_name = "Alex"
        self.print_system("✅ Voice print created successfully!")
        self.print_system("   • 95% accuracy in noisy environments")
        self.print_system("   • Unique voice fingerprint stored securely")
        self.print_system("   • Drone will ONLY respond to authorized voices")
        
        print("\n✨ Voice enrollment complete! The drone now knows your voice.")
        time.sleep(2)
    
    def navigation_demo(self):
        """Demonstrate navigation guidance"""
        print("\n" + "="*60)
        print("📝 STEP 2: NAVIGATION GUIDANCE")
        print("="*60)
        time.sleep(1)
        
        self.print_drone("Ready to guide you. Where would you like to go?")
        time.sleep(1)
        
        self.print_user("I need to find the bathroom")
        time.sleep(1)
        
        self.print_drone("I can see the bathroom is 12 meters ahead.")
        self.print_drone("Here's the path I've mapped:")
        
        # Show path visualization
        print("\n   🚪[You] ", end="")
        for i in range(12):
            if i == 5:
                print("🪑", end="")  # Chair obstacle
            elif i == 8:
                print("🚶", end="")  # Person
            else:
                print("⬆️", end="")
            time.sleep(0.2)
        print(" 🚻[Bathroom]\n")
        time.sleep(1)
        
        self.print_alert("Obstacle detected: chair at 5 meters")
        self.print_drone("Move slightly to your right to avoid the chair")
        time.sleep(1)
        
        # Update position
        self.position['x'] += 5
        self.position['floor_tiles_passed'] += 25
        self.show_position_awareness()
        time.sleep(1)
        
        self.print_alert("Person walking ahead at 8 meters")
        self.print_drone("Pausing briefly until they pass")
        time.sleep(2)
        
        self.position['x'] += 4
        self.position['floor_tiles_passed'] += 20
        
        self.print_drone("Path is clear now. Continuing forward.")
        time.sleep(1)
        
        self.print_drone("You've reached the bathroom. The door is opening now.")
        self.print_drone("I'll wait right here for you.")
    
    def obstacle_detection_demo(self):
        """Demonstrate obstacle detection and avoidance"""
        print("\n" + "="*60)
        print("📝 STEP 3: OBSTACLE DETECTION")
        print("="*60)
        time.sleep(1)
        
        self.print_user("What's around me right now?")
        time.sleep(1)
        
        # Show drone's vision
        print("\n🔍 DRONE CAMERA VIEW:")
        print("┌─────────────────────────────────────┐")
        print("│  🪑 TABLE    🚶 PERSON    🧱 WALL   │")
        print("│  2m ahead    5m ahead    8m ahead  │")
        print("│  [RIGHT]     [CENTER]    [LEFT]    │")
        print("└─────────────────────────────────────┘")
        time.sleep(2)
        
        self.print_drone("I detect:")
        self.print_drone("• A table 2 meters to your right")
        self.print_drone("• A person walking 5 meters ahead")
        self.print_drone("• A wall 8 meters ahead on the left")
        self.print_drone("• The path straight ahead is clear")
        
        time.sleep(1)
        self.print_user("Guide me around the table")
        
        self.print_drone("Moving slightly left to avoid the table")
        self.position['x'] += 1
        self.position['y'] -= 0.5
        
        self.print_drone("Table cleared. Now resuming original path.")
    
    def conversation_demo(self):
        """Demonstrate natural conversation with AI"""
        print("\n" + "="*60)
        print("📝 STEP 4: NATURAL CONVERSATION")
        print("="*60)
        time.sleep(1)
        
        # Show AI understanding
        self.print_system("🧠 AI BRAIN (GPT-4o) PROCESSING...")
        print("\n┌─────────────────────────────────────────┐")
        print("│  User: 'Is it safe to cross here?'      │")
        print("├─────────────────────────────────────────┤")
        print("│  AI Understanding:                       │")
        print("│  • Intent: Safety check before crossing │")
        print("│  • Context: User at intersection        │")
        print("│  • Action needed: Analyze traffic       │")
        print("└─────────────────────────────────────────┘")
        time.sleep(2)
        
        self.print_user("Is it safe to cross here?")
        time.sleep(1)
        
        self.print_drone("Let me check the traffic...")
        time.sleep(2)
        
        # Show sensor analysis
        print("\n📊 TRAFFIC ANALYSIS:")
        print("• Left: Vehicle approaching, 30m away")
        print("• Right: Clear")
        print("• Speed: 25 km/h")
        print("• Time to intersection: 4.3 seconds")
        time.sleep(2)
        
        self.print_drone("The street is clear for the next 4 seconds.")
        self.print_drone("You can cross now. I'll watch for vehicles and alert you.")
        
        time.sleep(1)
        self.print_user("Thank you. You're really helpful.")
        
        self.print_drone("You're welcome! I'm here to help you navigate safely.")
    
    def safety_features_demo(self):
        """Demonstrate safety features"""
        print("\n" + "="*60)
        print("📝 STEP 5: SAFETY FEATURES")
        print("="*60)
        time.sleep(1)
        
        self.battery = 25
        self.print_user("How's your battery?")
        time.sleep(1)
        
        self.print_drone(f"Battery at {self.battery}%. Time remaining: ~8 minutes.")
        self.print_alert("Low battery threshold reached!")
        
        print("\n🔄 AUTOMATED SAFETY PROTOCOL INITIATED")
        print("1. Searching for safe landing zone... ✓")
        print("2. Bench detected 3 meters ahead ✓")
        print("3. Guiding user to bench... ✓")
        time.sleep(2)
        
        self.print_drone("I'm guiding you to a bench where you can sit.")
        self.print_drone("It's 3 meters straight ahead.")
        time.sleep(1)
        
        self.print_drone("You're at the bench. I need to return to my charging station.")
        self.print_drone("I'll be back in 15 minutes. Say my name when you need me again.")
        
        # Demonstrate return-to-home
        print("\n🏠 RETURN-TO-HOME ACTIVATED")
        print("• Calculating path back to charging station... ✓")
        print("• Maintaining safe altitude... ✓")
        print("• Avoiding obstacles... ✓")
        print("• Reached charging station ✓")
        time.sleep(2)
    
    def market_opportunity_slide(self):
        """Show market data for the pitch"""
        print("\n" + "="*60)
        print("📊 MARKET OPPORTUNITY")
        print("="*60)
        
        print("""
🌍 GLOBAL STATISTICS:
   • 285 million visually impaired people worldwide
   • 39 million completely blind
   • $7.8 billion assistive technology market
   • 15% annual growth rate

💰 CURRENT SOLUTIONS:
   • Guide Dog: $40,000 + 2-year wait
   • Smart Cane: $500 - limited range
   • Human Assistant: $15-20/hour

🚀 AEROGUIDE ADVANTAGE:
   • Hardware: $299 (off-the-shelf drone)
   • Software: $99/year subscription
   • Available NOW - no training/waiting
   • 30-day money-back guarantee
        """)
    
    def technical_architecture_slide(self):
        """Show technical diagram"""
        print("\n" + "="*60)
        print("🔧 TECHNICAL ARCHITECTURE")
        print("="*60)
        
        print("""
┌─────────────────────────────────────────────────────┐
│                 AEROGUIDE SYSTEM                      │
├─────────────────────────────────────────────────────┤
│                                                       │
│  👤 USER → 🎤 Voice → ✅ Speaker Verification        │
│                              ↓                        │
│                    🧠 AI BRAIN (GPT-4o)              │
│                    • Understands intent              │
│                    • Generates responses             │
│                    • Plans navigation                │
│                    ↓                        ↓        │
│           🗣️ Voice Feedback    🚁 Drone Actions      │
│                                                       │
│  📍 POSITION AWARENESS:                               │
│  • Floor tracking camera (optical flow)              │
│  • TOF distance sensors                              │
│  • Voice direction detection                          │
│  • Accuracy: ±10cm                                    │
│                                                       │
└─────────────────────────────────────────────────────┘
        """)
    
    def run_complete_pitch(self):
        """Run the complete simulation for the pitch"""
        
        # Title screen
        print("\033[96m" + "="*70 + "\033[0m")
        print("\033[96m🚁 AEROGUIDE: AI-POWERED DRONE COMPANION FOR THE BLIND\033[0m")
        print("\033[96m" + "="*70 + "\033[0m")
        print("\nAeroHack-BlindCompanion Team")
        print("AERo-pitch Challenge 2026")
        time.sleep(2)
        
        # Demo sequence
        self.enroll_demo()
        input("\nPress Enter to continue to Navigation Demo...")
        
        self.navigation_demo()
        input("\nPress Enter to continue to Obstacle Detection...")
        
        self.obstacle_detection_demo()
        input("\nPress Enter to continue to Conversation Demo...")
        
        self.conversation_demo()
        input("\nPress Enter to continue to Safety Features...")
        
        self.safety_features_demo()
        input("\nPress Enter to see Technical Architecture...")
        
        self.technical_architecture_slide()
        input("\nPress Enter to see Market Opportunity...")
        
        self.market_opportunity_slide()
        
        # Closing
        print("\n" + "="*70)
        print("✅ DEMONSTRATION COMPLETE")
        print("="*70)
        print("""
🎯 KEY TAKEAWAYS:
✓ Voice recognition - Only responds to authorized user
✓ Position awareness - Knows exact location without GPS
✓ Obstacle detection - Sees and avoids obstacles
✓ Natural conversation - Understands context, not just commands
✓ Safety features - Automatic return-to-home, low battery alerts
✓ Market ready - Uses existing hardware, affordable subscription

🤝 Thank you for your attention! We're ready for questions.
        """)


if __name__ == "__main__":
    # Run the pitch simulation
    simulation = AeroGuidePitchSimulation()
    simulation.run_complete_pitch()