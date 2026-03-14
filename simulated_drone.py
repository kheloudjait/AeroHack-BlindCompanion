import pygame
import sys

class SimulatedDrone:

    def __init__(self):
        self.x = 400
        self.y = 300
        self.height = 0
        self.flying = False

    def takeoff(self):
        self.flying = True
        self.height = 100
        print("Drone taking off")

    def land(self):
        self.flying = False
        self.height = 0
        print("Drone landing")

    def move_forward(self, cm):
        self.y -= cm
        print(f"Drone moved forward {cm} cm")

    def move_back(self, cm):
        self.y += cm
        print(f"Drone moved back {cm} cm")

    def move_left(self, cm):
        self.x -= cm
        print(f"Drone moved left {cm} cm")

    def move_right(self, cm):
        self.x += cm
        print(f"Drone moved right {cm} cm")

    def rotate_clockwise(self, deg):
        print(f"Drone rotated {deg} degrees")

    def rotate_counter_clockwise(self, deg):
        print(f"Drone rotated {-deg} degrees")

    def get_battery(self):
        return 85

    def get_height(self):
        return self.height
