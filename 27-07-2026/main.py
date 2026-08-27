import time
import socket
from machine import Pin
import libs.leds
import libs.motion
import libs.pid
import libs.sensors

robot_driver = libs.motion.MecanumDriver()
line_tracker = libs.sensors.LineSensors3Pin(pin_left=35, pin_mid=36, pin_right=39)

# Balanced PID settings for torque and stability
pid = libs.pid.PIDController(
    kp=0.20,
    ki=0.0,
    kd=0.02,
    output_limits=(-200, 200)
)

SETPOINT = 2000
BASE_SPEED = 450   # Overcomes static motor/wheel friction
DEADBAND = 35

def apply_power_saving():
    print("\n[POWER] Movement finished. Activating Idling...")
    robot_driver.halt()
    robot_driver.disable_driver()
    libs.leds.start_blink_indicator()
    print("[POWER] Motor Driver Suspended.")

def wake_up_systems():
    libs.leds.stop_blink_indicator()
    robot_driver.enable_driver()
    print("[POWER] Systems awake!")

def strafe_left():
    print("\nSTRAFING SIDEWAYS left\n")
    robot_driver.drive(robot_driver.STRAFE_LEFT, speed=450)
    time.sleep(3)
    robot_driver.halt()

def manual_move_robot():
    wake_up_systems()
    print("\n Moving forward ..")
    robot_driver.drive(robot_driver.FORWARD, speed=450)
    time.sleep(3)
    robot_driver.halt()
    
    print("\nSTRAFING SIDEWAYS left\n")
    robot_driver.drive(robot_driver.STRAFE_LEFT, speed=450)
    time.sleep(3)
    robot_driver.halt()
    
    print("\n Coming back\n")
    robot_driver.drive(robot_driver.STRAFE_RIGHT, speed=450)
    time.sleep(3)
    robot_driver.halt()
    
    robot_driver.drive(robot_driver.BACKWARD, speed = 450)
    time.sleep(3)
    robot_driver.halt()
    
    print("\n ---- MISSION COMPLETE ---\n ")
    apply_power_saving()
    
def track_line(timeout_ms=500):
    wake_up_systems()
    print("\n[SYSTEM] --- Starting AGV Line Tracking ---")
    robot_driver._shift_out(robot_driver.FORWARD)
    pid.reset()
    
    no_line_start = None
    
    while True:
        position, line_detected = line_tracker.get_position()
        
        if not line_detected:
            if no_line_start is None:
                no_line_start = time.ticks_ms()
            elif time.ticks_diff(time.ticks_ms(), no_line_start) > timeout_ms:
                print("\n[SYSTEM] --- End of Line Reached. Stopping AGV ---")
                break
        else:
            no_line_start = None
        
        error = SETPOINT - position
        
        if abs(error) < DEADBAND:
            correction = 0
            pid.reset()  # Reset terms so error doesn't build up during deadband
        else:
            correction = pid.compute(error)
        
        left_speed = BASE_SPEED - correction
        right_speed = BASE_SPEED + correction
        
        # Clamp speeds within valid PWM boundaries
        left_speed = int(max(0, min(1023, left_speed)))
        right_speed = int(max(0, min(1023, right_speed)))
        
        robot_driver.pwm1.duty(left_speed)
        robot_driver.pwm2.duty(right_speed)
        
        time.sleep_ms(10)
    
    robot_driver.halt()
    apply_power_saving()

if __name__ == "__main__":
    #track_line()
    strafe_left()
    manual_move_robot()
    
    
    """print("STARTING")
    print("STARTING")
    print("STARTING")
    print("STARTING")
    print("\n Moving forward ..")
    robot_driver.drive(robot_driver.FORWARD, speed=600)
    time.sleep(3)
    robot_driver.halt()"""
