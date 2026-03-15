"""
Simple test version - Guaranteed to work
"""

from drone import Drone
from simulator import Simulator

# Print to confirm script is running
print("🚀 Starting Drone Program...")
print("Press Ctrl+C to stop")

# Initialize drone and simulator
drone = Drone()
sim = Simulator(drone)

# Run the simulator
print("🖥️ Opening simulator window...")
sim.run()

print("👋 Program ended")