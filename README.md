===============================================
Acebot Autonomous Warehouse AGV
===============================================

  ### Description
An autonomous, data-driven Automated Guided Vehicle(AGV) prototype built using the ESP32 microcontroller and programmed in MicroPython. Designed for indoor warehouse logistics, this robot navigages a grid environment using bottom-mounted IR line-tracking sensors, utilizes an ultrasonic distance sensor mounted on a scanning servo turret for dynamic objstacle intervention, and implements a Finite State Machine (FSM) to conserve battery health during operational downtime

   ### Hardware Specificaation & Pin Mapping

1. ## Drive & Locomotion (Mecanum setup via 74HC595 shift register)
- PWM1(GPIO 19): Left_side motor speed control (500Hz baseline)
- PWM2(GPIO 23): Right-side motor speed control (500Hz baseline)
- EN (GPIO 16): Driver H-bridge Output Enable (Active Low). Pulling HIGH suspends standby current
- Data(GPIO 5): Serial data input bit stream
- SHCP(GPIO 18): Shift Register Clock Pulse
- STCP (GPIO 17): Storage Register Clock Pulse (Latch)

2. ## Guidance & Threat Detection

- Left Tracking Sensor (GPIO 35): Analog-to-Digital (ADC) input channel
- Middle Tracking Sensor (GPIO 36): Analog-to-Digital (ADC) input channel
- Right Tracking Sensor (GPIO 39): Analog-to-Digital (ADC) input channel
-Servo Control Signal (GPIO 25): 50Hz PWM position channel for the turret
- Ultrasonic Trigger (GPIO 13): Sends the 10-microsecond measurement pulse
- Ultrasonic Echo (GPIO 14): Captures the return bounce timing window

3. ## Human-Machine Interface (HMI)
- Left Indicator LED (GPIO 2): Diagnostic flashing
- Right Indicator LED (GPIO 12): Diagnostic flashing
- Notification Buzzer (GPIO 33): High-frequency audio alerts


### Finite State Machine Logic
To ensure deterministic reliability and prevent power wastage, the main control sequence transitions dynamically between four lifecylces modes: 

0. IDLE (Standby Power Mode): The robot rests at a dock awaiting job allocations over serial/terminal input. To conserve battery life, the motor driver EN pin is pulled HIGH, the servo signal is detached via software, buzzer duty cycle is forced to 0.

1. NAVIGATING (Active Transport): The system tracks warehouse ground grids via the ADC IR arrays and continuously poles the front sonar turret for safetly cross-sections.

2. OBSTACLE_AVOIDANCE (Hazard intervention): if an object is detected within 20cm, the robot halts immediately and pulses the buzzer until the path is cleared

3. PICK_DROP (Station Operation): Triggered upon reaching a destination intersection coordinate, simulating a cargo transfer event within distinct audible alert profiles before returning to IDLE