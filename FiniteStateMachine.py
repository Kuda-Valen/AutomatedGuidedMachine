import time
import random
from enum import Enum

# Phase One: Define Operational States (FSM)
class AGVState(Enum):
    """ Enumeration class defining all operational states."""
    STATE_FORWARD = 1
    STATE_BRAKE = 2
    STATE_REVERSE = 3
    STATE_SCAN = 4


"""
    Core Robotics Architecture Class
"""

class AGVArchitecture:
    def __init__(self):
        # current logic state
        self.current_state = AGVState.STATE_FORWARD

        self.sensor_buffer = []
        self.buffer_size = 5
        self.raw_distance = 0
        self.filtered_distance = 0

        # Safety thresholds
        self.STOP_THRESHOLD_CM = 30
        self.SAFE_THRESHOLD_CM = 50

    # The Non-Blocking Filter Logic
    # (Median Filter Implementation)

    def apply_median_filter(self, new_reading):
        """
            Receives raw sensor reading, adds it to the buffer,
            and returns the median of the buffer
        """

        self.sensor_buffer.append(new_reading)

        # Maintain the buffer size
        if len(self.sensor_buffer) > self.buffer_size:
            self.sensor_buffer.pop(0)   # We remove the oldest reading

        # Wait for the buffer to fill before filtering
        if len(self.sensor_buffer) < self.buffer_size:
            return 999.0                # Placeholder distance while waiting

        # Create a sorted copy to find the median without disturbing original buffer
        sorted_buffer = sorted(self.sensor_buffer)

        # Since size is odd (5), median is index 2
        median_value = sorted_buffer[2]
        return median_value

    # Finite State Machine Decision Logic
    def execute_state_machine(self, clean_distance):
        """
            Interprets the filtered sensor data and manages
            transitions between operational states.
        """
        self.filtered_distance = clean_distance

        # Define transitions and required actions for each state
        if self.current_state == AGVState.STATE_FORWARD:
            # Check for immediate danger
            if self.filtered_distance < self.STOP_THRESHOLD_CM:
                print(f"!!! OBSTACLE DETECTED at {self.filtered_distance:.1fm}cm !!!")
                self.action_cut_motors()
                self.current_state = AGVState.STATE_BRAKE
            else:
                self.action_drive_forward()

        elif self.current_state == AGVState.STATE_BRAKE:
            # In a Real Robot, we would introduce a non-blocig pause here.
            # For now we transition immediately to maneuvering.
            print("--- AGV HALTED, PREPARING MANEUVER ---")
            self.current_state = AGVState.STATE_REVERSE

        elif self.current_state == AGVState.STATE_REVERSE:
            # Reversing logic to clear the obstacle path
            self.action_drive_reverse()

            # If path seems clear based on the sensor, try moving forward again
            if self.filtered_distance > self.SAFE_THRESHOLD_CM:
                print(f"--- PATH CLEAR ({self.filtered_distance:.1f}cm), RESUMING MISSION ---")
                self.current_state = AGVState.STATE_FORWARD
                 