import pygame
import threading
import speech_recognition as sr
import os
import time

# OpenAI v1+ uses a different API surface than older versions.
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class AIDroneBrain:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        if OpenAI is not None and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        # Force fallback for now
        self.client = None
        self.context = "You are a helpful drone companion for a blind person. Respond with a short message and an action from: TAKEOFF, MOVE_FORWARD, MOVE_BACK, MOVE_LEFT, MOVE_RIGHT, LAND, HOVER. Format: Message. ACTION: ACTION_NAME"

    def get_ai_response(self, user_text):
        # Simple keyword fallback when OpenAI client is missing.
        if self.client is None:
            if "hello" in user_text or "hi" in user_text or "awake" in user_text:
                return "Good morning! I'm ready to help. Say 'find my glasses' or 'move forward'.", "TAKEOFF"
            # Navigation commands: if you mention a known object, guide there
            for obj in ["table", "door", "chair"]:
                if obj in user_text:
                    return "", f"GUIDE_{obj}"

            if "glasses" in user_text:
                return "I see a pair of glasses on the table ahead.", "LOCATE_table"

            # Note/Fridge query (static info response)
            if ("note" in user_text or "notes" in user_text or "news" in user_text) and "fridge" in user_text:
                return ("Yes, there's a poster left by your collocataire on the fridge where it says: 'I bought some cheese'.", "HOVER")

            if "forward" in user_text or "go forward" in user_text:
                return "Moving forward.", "MOVE_FORWARD"
            if "back" in user_text or "reverse" in user_text:
                return "Moving back.", "MOVE_BACK"
            if "left" in user_text:
                return "Moving left.", "MOVE_LEFT"
            if "right" in user_text:
                return "Moving right.", "MOVE_RIGHT"
            if "land" in user_text or "stop" in user_text:
                return "Landing now.", "LAND"
            # Generic response for unknown commands
            return "I'm listening. Ask me to move, find objects, or land.", "HOVER"

        # Otherwise use OpenAI for a more intelligent response
        try:
            response = self.client.responses.create(
                model="gpt-3.5-turbo",
                input=f"{self.context}\nUser: {user_text}"
            )

            # Extract text output generically
            ai_text = ""
            if hasattr(response, "output_text") and response.output_text:
                ai_text = response.output_text
            elif hasattr(response, "output"):
                for item in response.output:
                    if isinstance(item, dict) and "content" in item:
                        for chunk in item["content"]:
                            if isinstance(chunk, dict) and "text" in chunk:
                                ai_text += chunk["text"]
                            elif isinstance(chunk, str):
                                ai_text += chunk

            ai_text = ai_text.strip()

            # Parse action
            if "ACTION: TAKEOFF" in ai_text:
                action = "TAKEOFF"
            elif "ACTION: MOVE_FORWARD" in ai_text:
                action = "MOVE_FORWARD"
            elif "ACTION: MOVE_BACK" in ai_text:
                action = "MOVE_BACK"
            elif "ACTION: MOVE_LEFT" in ai_text:
                action = "MOVE_LEFT"
            elif "ACTION: MOVE_RIGHT" in ai_text:
                action = "MOVE_RIGHT"
            elif "ACTION: LAND" in ai_text:
                action = "LAND"
            else:
                action = "HOVER"

            # Remove action from text
            message = ai_text.split("ACTION:")[0].strip()
            return message, action
        except Exception as e:
            print(f"AI Error: {e}")
            return "I'm sorry, I didn't catch that.", "HOVER"

class Simulator:
    def __init__(self, drone):
        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("AeroHack: Blind Companion v1.2")
        self.drone = drone
        self.clock = pygame.time.Clock()
        self.running = True

        # Room Walls and Furniture (Obstacles)
        self.obstacles = [
            {"name": "table", "rect": pygame.Rect(100, 100, 100, 100), "color": (139, 69, 19)},
            {"name": "door", "rect": pygame.Rect(350, 0, 100, 20), "color": (255, 255, 255)},
            {"name": "chair", "rect": pygame.Rect(600, 400, 40, 40), "color": (100, 100, 100)}
        ]

        self.font = pygame.font.SysFont(None, 24)

        self.ai_brain = AIDroneBrain()

        # Navigation target (object name)
        self.navigation_target = None
        # Navigation guidance state (to avoid repeating the same instructions too frequently)
        self._last_nav_hint = ""
        self._last_nav_time = 0.0
        self._nav_interval = 0.5  # seconds between guidance updates

        try:
            self.start_voice_engine()
        except Exception as e:
            print(f"Voice system failed to start: {e}. Simulation will run without voice commands.")

    def draw_environment(self):
        # Floor Grid
        for i in range(0, 800, 50):
            pygame.draw.line(self.screen, (60, 60, 60), (i, 0), (i, 600))
        for j in range(0, 600, 50):
            pygame.draw.line(self.screen, (60, 60, 60), (0, j), (800, j))

        # Draw Obstacles
        for obs in self.obstacles:
            pygame.draw.rect(self.screen, obs["color"], obs["rect"])
            pygame.draw.rect(self.screen, (120, 120, 130), obs["rect"], 2)

    def draw_drone(self):
        # 1. Draw "Sensor Ping" (The drone's vision)
        if self.drone.flying:
            ping_color = (255, 255, 0, 50) if self.drone.alert else (0, 255, 0, 30)
            s = pygame.Surface((self.drone.sensor_range*2, self.drone.sensor_range*2), pygame.SRCALPHA)
            pygame.draw.circle(s, ping_color, (self.drone.sensor_range, self.drone.sensor_range), self.drone.sensor_range, 1)
            self.screen.blit(s, (self.drone.x - self.drone.sensor_range, self.drone.y - self.drone.sensor_range))

        # 2. Drone Body
        color = (255, 0, 0) # Grounded
        if self.drone.flying:
            color = (255, 165, 0) if self.drone.alert else (0, 255, 0)
        
        pygame.draw.circle(self.screen, color, (int(self.drone.x), int(self.drone.y)), self.drone.radius)

        # Draw speech bubble if there's a message
        if self.drone.message:
            text_surf = self.font.render(self.drone.message, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(int(self.drone.x), int(self.drone.y - 40)))
            bg_rect = text_rect.inflate(10, 10)
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 2)
            self.screen.blit(text_surf, text_rect)

    def start_voice_engine(self):
        threading.Thread(target=self.listen_for_speech, daemon=True).start()

    def listen_for_speech(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Voice System Active: Talk to your AI drone companion!")
            
            while self.running:
                try:
                    audio = recognizer.listen(source, phrase_time_limit=5)
                    text = recognizer.recognize_google(audio).lower()
                    print(f"I heard: {text}")
                    
                    # Get AI response and action
                    response_text, action = self.ai_brain.get_ai_response(text)
                    
                    # Drone speaks the AI's response (if any)
                    if response_text:
                        self.drone.speak(response_text)
                    
                    # Perform the action
                    if action == "TAKEOFF":
                        self.drone.takeoff()
                    elif action in ("MOVE_FORWARD", "MOVE_BACK", "MOVE_LEFT", "MOVE_RIGHT"):
                        # Auto takeoff if the drone isn't already flying
                        if not self.drone.flying:
                            self.drone.takeoff()
                        if action == "MOVE_FORWARD":
                            self.drone.move(0, -1, self.obstacles)
                        elif action == "MOVE_BACK":
                            self.drone.move(0, 1, self.obstacles)
                        elif action == "MOVE_LEFT":
                            self.drone.move(-1, 0, self.obstacles)
                        elif action == "MOVE_RIGHT":
                            self.drone.move(1, 0, self.obstacles)
                    elif action == "LAND":
                        self.drone.land()
                    elif action == "LOCATE_table":
                        # Message already spoken, glasses located on table
                        pass
                    elif action.startswith("GUIDE_") or action.startswith("NAVIGATE_"):
                        target_name = action.split("_", 1)[1]  # Works for both GUIDE_ and NAVIGATE_
                        target = next((o for o in self.obstacles if o["name"] == target_name), None)
                        if target:
                            # Auto takeoff if not flying
                            if not self.drone.flying:
                                self.drone.takeoff()
                            # Set navigation target for autonomous movement
                            self.navigation_target = target_name
                            # Provide initial guidance
                            self._speak_navigation_guidance(target, force=True)
                except sr.UnknownValueError:
                    pass
                except Exception as e:
                    print(f"Mic error: {e}")

    def _get_navigation_goal_point(self, target, margin=10):
        """Pick a reachable point near the obstacle so the drone can 'arrive' without colliding."""
        rect = target["rect"]
        goal_x = self.drone.x
        goal_y = self.drone.y

        # Approach from the closest side of the object
        if self.drone.x < rect.left:
            goal_x = rect.left - margin
        elif self.drone.x > rect.right:
            goal_x = rect.right + margin

        if self.drone.y < rect.top:
            goal_y = rect.top - margin
        elif self.drone.y > rect.bottom:
            goal_y = rect.bottom + margin

        return goal_x, goal_y

    def _format_navigation_hint(self, target, goal_x, goal_y):
        dx = goal_x - self.drone.x
        dy = goal_y - self.drone.y

        # Convert screen pixels to rough meters (50 px ~= 1 meter)
        meters_x = abs(dx) / 50.0
        meters_y = abs(dy) / 50.0

        # Round to nearest 0.5m to avoid rapid jitter in spoken guidance
        meters_x = round(meters_x * 2) / 2
        meters_y = round(meters_y * 2) / 2

        parts = []
        if meters_y >= 0.5:
            direction = "forward" if dy < 0 else "back"
            parts.append(f"{meters_y:.1f} meters {direction}")
        if meters_x >= 0.5:
            direction = "right" if dx > 0 else "left"
            if parts:
                parts.append(f"then {meters_x:.1f} meters {direction}")
            else:
                parts.append(f"{meters_x:.1f} meters {direction}")

        if not parts:
            return None
        return ", ".join(parts)

    def _speak_navigation_guidance(self, target, force=False):
        if not target:
            return
        goal_x, goal_y = self._get_navigation_goal_point(target)
        hint = self._format_navigation_hint(target, goal_x, goal_y)
        if not hint:
            return

        # Avoid speaking the same guidance repeatedly (hint is rounded)
        now = time.time()
        if not force and hint == self._last_nav_hint and (now - self._last_nav_time) < self._nav_interval:
            return

        self._last_nav_hint = hint
        self._last_nav_time = now
        message = f"Moving towards the {target['name']}: go {hint}."
        self.drone.speak(message)

    def _step_navigation(self):
        """Move the drone automatically toward the current navigation target."""
        target = next((o for o in self.obstacles if o["name"] == self.navigation_target), None)
        if not target:
            return

        # Compute a reachable goal point just outside the obstacle
        goal_x, goal_y = self._get_navigation_goal_point(target)

        # Stop when we are close enough to the goal point
        if abs(self.drone.x - goal_x) <= self.drone.speed and abs(self.drone.y - goal_y) <= self.drone.speed:
            self.navigation_target = None
            self._last_nav_message = ""
            self.drone.speak(f"Arrived at the {target['name']}.")
            return

        # Periodically provide navigation guidance so the user can follow along
        self._speak_navigation_guidance(target, force=True)

        # Determine basic direction toward the goal (slow down during navigation)
        nav_speed = max(1, int(self.drone.speed * 0.4))
        dx = 0
        dy = 0
        if abs(self.drone.x - goal_x) > nav_speed:
            dx = 1 if goal_x > self.drone.x else -1
        if abs(self.drone.y - goal_y) > nav_speed:
            dy = 1 if goal_y > self.drone.y else -1

        # When navigating, move in smaller steps for smoother guidance.
        moved = self.drone.move(dx * 0.5, dy * 0.5, self.obstacles)
        if not moved:
            # Try moving along one axis at a time to avoid simple obstacles
            if dx != 0 and dy != 0:
                if self.drone.move(dx, 0, self.obstacles):
                    return
                if self.drone.move(0, dy, self.obstacles):
                    return

            # Stuck: stop navigation and ask the user to reposition
            self.navigation_target = None
            self._last_nav_message = ""
            self.drone.speak(f"I can't reach the {target['name']} from here. Please reposition me or try a different direction.")

    def run(self):
        while self.running:
            self.screen.fill((20, 20, 20))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False

            # Input Handling (optional, for testing)
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_t]: self.drone.takeoff()
            if keys[pygame.K_l]: self.drone.land()
            if keys[pygame.K_UP]: dy = -1
            if keys[pygame.K_DOWN]: dy = 1
            if keys[pygame.K_LEFT]: dx = -1
            if keys[pygame.K_RIGHT]: dx = 1

            # If the AI set a navigation target, move toward it automatically
            if self.navigation_target:
                self._step_navigation()
            else:
                self.drone.move(dx, dy, self.obstacles)

            self.drone.clear_message_if_needed()
            
            self.draw_environment()
            self.draw_drone()
            
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
