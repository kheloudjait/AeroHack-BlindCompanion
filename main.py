# main.py
from simulated_drone import SimulatedDrone

def main():
    drone = SimulatedDrone()
    print("🚀 Simulated Drone Ready!")
    print("Commands: takeoff, land, forward, back, left, right, rotate_cw, rotate_ccw, battery, height, exit")

    while True:
        cmd = input("Enter command: ").strip().lower()

        if cmd == "takeoff":
            drone.takeoff()
        elif cmd == "land":
            drone.land()
        elif cmd == "forward":
            drone.move_forward(20)
        elif cmd == "back":
            drone.move_back(20)
        elif cmd == "left":
            drone.move_left(20)
        elif cmd == "right":
            drone.move_right(20)
        elif cmd == "rotate_cw":
            drone.rotate_clockwise(45)
        elif cmd == "rotate_ccw":
            drone.rotate_counter_clockwise(45)
        elif cmd == "battery":
            print(f"Battery: {drone.get_battery()}%")
        elif cmd == "height":
            print(f"Height: {drone.get_height()} cm")
        elif cmd == "exit":
            print("Exiting simulation")
            break
        else:
            print("Unknown command")

        drone.update_display()

if __name__ == "__main__":
    main()
