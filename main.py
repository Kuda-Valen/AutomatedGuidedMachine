import time
import libs.motion

# We instantiate our custom driver object
robot_driver = libs.motion.MecanumDriver()

print("\n=== Custom MOtion Engine Loaded \n")

print("1. Moving forward at 50% speed....")
robot_driver.drive(robot_driver.FORWARD, speed=512)
time.sleep(2)

print("Straffing sideways left....")
robot_driver.drive(robot_driver.STRAFE, speed=600)
time.sleep(1.5)

print("Mission Complete. Parking")
robot_driver.halt()