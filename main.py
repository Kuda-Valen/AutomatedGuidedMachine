import time
import socket
import machine
from machine import Pin
import libs.motion
import libs.telemetry
import libs.leds
import libs.sensors
import libs.pid

# ==========================================
# HARDWARE INITIALIZATION
# ==========================================
robot_driver = libs.motion.MecanumDriver()

line_tracker = libs.sensors.LineSensors3Pin(
    pin_left=35,
    pin_mid=36,
    pin_right=39,
    threshold=2300
)

# Power Saving & Helper functions
def apply_power_saving():
    """Shuts down high-current systems dynamically to preserve battery"""
    print("\n[POWER] Movement finished. Activating automated standby idle..")
    robot_driver.halt()
    Pin(16, Pin.OUT).on()
    
    libs.leds.start_blink_indicator()
    print("[POWER] Motor driver suspended. Background heartbeat indicator active.\n")

def wake_up_systems():
    """Wakes up motor driver hardware and stops idle indicators"""
    libs.leds.stop_blink_indicator()
    Pin(16, Pin.OUT).off()
    print("[POWER] Systems awake. Ready for locomotion..")

# ==========================================
# INTERSECTION / NODE MANEUVERS
# ==========================================
def execute_intersection_turn(direction="STRAIGHT", speed=350):
    """
    Executes precise maneuvers at warehouse intersections.
    Directions supported: 'STRAIGHT', 'LEFT', 'RIGHT', 'STRAFE_LEFT', 'STRAFE_RIGHT'
    """
    print(f"[NAV] Executing Intersection Node Action: {direction}")
    
    if direction == "STRAIGHT":
        # Drive forward slightly to clear the perpendicular intersection line
        robot_driver.drive(robot_driver.FORWARD, speed=speed)
        time.sleep(0.3)
        
    elif direction == "LEFT":
        # 1. Drive forward slightly to align rotation axis over intersection center
        robot_driver.drive(robot_driver.FORWARD, speed=speed)
        time.sleep(0.2)
        # 2. Pivot left until Middle sensor re-acquires the main line
        robot_driver.drive(robot_driver.STRAFE_LEFT, speed=speed + 100)
        time.sleep(0.4) # Initial blind burst out of node
        
        # Scan until middle sensor lands back on the black tape
        start_time = time.time()
        while time.time() - start_time < 2.0:
            _, mid_on, _ = line_tracker.read_digital()
            if mid_on:
                print("[NAV] Line re-acquired after LEFT turn.")
                break
            time.sleep(0.01)

    elif direction == "RIGHT":
        robot_driver.drive(robot_driver.FORWARD, speed=speed)
        time.sleep(0.2)
        robot_driver.drive(robot_driver.STRAFE_RIGHT, speed=speed + 100)
        time.sleep(0.4)
        
        start_time = time.time()
        while time.time() - start_time < 2.0:
            _, mid_on, _ = line_tracker.read_digital()
            if mid_on:
                print("[NAV] Line re-acquired after RIGHT turn.")
                break
            time.sleep(0.01)

    robot_driver.halt()
    time.sleep(0.1) # Brief pause for chassis stabilization

# ==========================================
# 1. ENHANCED AUTONOMOUS LINE FOLLOWING (FSM)
# ==========================================
def run_agv_line_following(speed=350, node_action="STRAIGHT"):
    """
    Primary FSM Line Following Method.
    Maintains centered line position and executes turn actions when nodes are hit.
    """
    wake_up_systems()
    print(f"[AGV] Starting FSM line following (Node Mode: {node_action})... Press Ctrl+C to stop.")
    
    intersection_count = 0
    
    try:
        while True:
            left_on, mid_on, right_on = line_tracker.read_digital()
            
            # STATE 1: PERFECTLY CENTERED -> Drive Straight
            if mid_on and not left_on and not right_on:
                robot_driver.drive(robot_driver.FORWARD, speed=speed)
                
            # STATE 2: SLIGHT DRIFT RIGHT -> Gentle Correction
            elif left_on and mid_on and not right_on:
                robot_driver.drive(robot_driver.FORWARD, speed=max(200, speed - 100))
                
            # STATE 3: HARD DRIFT RIGHT -> Strafe Left
            elif left_on and not mid_on and not right_on:
                robot_driver.drive(robot_driver.STRAFE_LEFT, speed=speed)
                
            # STATE 4: SLIGHT DRIFT LEFT -> Gentle Correction
            elif right_on and mid_on and not left_on:
                robot_driver.drive(robot_driver.FORWARD, speed=max(200, speed - 100))
                
            # STATE 5: HARD DRIFT LEFT -> Strafe Right
            elif right_on and not mid_on and not left_on:
                robot_driver.drive(robot_driver.STRAFE_RIGHT, speed=speed)
                
            # STATE 6: INTERSECTION / AISLE NODE DETECTED (All 3 Sensors on Black)
            elif left_on and mid_on and right_on:
                intersection_count += 1
                print(f"\n[NODE] Node #{intersection_count} reached!")
                
                # Halt momentarily to prevent momentum drift
                robot_driver.halt()
                time.sleep(0.1)
                
                # Execute specified turn routine
                execute_intersection_turn(direction=node_action, speed=speed)
                
            # STATE 7: LINE LOST (All sensors see White)
            else:
                robot_driver.halt()
                
            time.sleep(0.01) # 100 Hz Loop Execution Rate

    except KeyboardInterrupt:
        print("\n[AUTO] Navigation manually aborted.")
        
    robot_driver.halt()
    apply_power_saving()

# ==========================================
# 2. HELPER FUNCTIONS & TELEMETRY
# ==========================================
def parse_network_command(raw_data):
    """
    Parses incoming socket data.
    Expects formats like: "FORWARD", "AUTO", "AUTO:LEFT", "STOP"
    """
    try:
        clean_string = raw_data.decode('utf-8').strip().upper()
        
        if not clean_string:
            return None, None
        
        if ":" in clean_string:
            parts = clean_string.split(":", 1)
            command = parts[0]
            param = parts[1]
            return command, param
        else:
            return clean_string, None
        
    except Exception as e:
        print(f"[PARSER ERROR] Failed to parse data: {e}")
        return None, None

def manual_move_robot():
    """Diagnostic manual routine"""
    wake_up_systems()
    print("1. Moving forward at 50% speed....")
    robot_driver.drive(robot_driver.FORWARD, speed=512)
    time.sleep(1.5)
    robot_driver.halt()

    print("\n===== Strafing sideways left....====\n")
    robot_driver.drive(robot_driver.STRAFE_LEFT, speed=600)
    time.sleep(1)
    robot_driver.halt()

    print("\n=== Coming Back ===\n")
    robot_driver.drive(robot_driver.STRAFE_RIGHT, speed=600)
    time.sleep(1)
    robot_driver.halt()

    robot_driver.drive(robot_driver.BACKWARD, speed=512)
    time.sleep(1.5)
    robot_driver.halt()

    print("\n====Mission Complete. Parking ========\n")
    apply_power_saving()

def move_front():
    wake_up_systems()
    print("[SYSTEM]   -- MOVING FORWARD ---")
    robot_driver.drive(robot_driver.FORWARD, speed=1000)
    time.sleep(7)
    robot_driver.halt()
    print("[SYSTEM]   -- MISSION COMPLETE ---")
    apply_power_saving()
    
# ==========================================
# 3. NETWORK CONTROL & MAIN EXECUTION
# ==========================================
def wifi_connection():
    WIFI_SSID = "Mukwasi 2G"
    WIFI_PASS = "Mukwasi123"

    wifi = libs.telemetry.WifiEngine(WIFI_SSID, WIFI_PASS)

    if not wifi.connect():
        print("[ERROR] Could not connect to network. Exiting.")
        raise SystemExit

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8080))
    server_socket.listen(1)
    print("\n[SERVER] Listening for wireless commands on port 8080...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"\n[SERVER] Connection established from: {client_address}")
            
            wake_up_systems()
            
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                command, param = parse_network_command(data)
                
                if not command:
                    continue
                    
                print(f"[EXECUTE] Command: {command} | Parameter: {param}")
                
                if command == "FORWARD":
                    speed = int(param) if param and param.isdigit() else 512
                    robot_driver.drive(robot_driver.FORWARD, speed=speed)
                elif command == "BACKWARD":
                    speed = int(param) if param and param.isdigit() else 512
                    robot_driver.drive(robot_driver.BACKWARD, speed=speed)
                elif command == "LEFT":
                    speed = int(param) if param and param.isdigit() else 512
                    robot_driver.drive(robot_driver.STRAFE_LEFT, speed=speed)
                elif command == "RIGHT":
                    speed = int(param) if param and param.isdigit() else 512
                    robot_driver.drive(robot_driver.STRAFE_RIGHT, speed=speed)
                elif command == "STOP":
                    robot_driver.halt()
                elif command == "AUTO":
                    # Accepts node commands like "AUTO:LEFT", "AUTO:RIGHT", "AUTO:STRAIGHT"
                    action = param if param in ["LEFT", "RIGHT", "STRAIGHT"] else "STRAIGHT"
                    run_agv_line_following(speed=350, node_action=action)
                else:
                    print(f"[WARN] Unknown command format: {command}")
            
            client_socket.close()
            print("[SERVER] Client disconnected. Waiting for next controller...")
            apply_power_saving()

    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down network listener")
        robot_driver.halt()
        server_socket.close()
        wifi.disconnect()

if __name__ == "__main__":
    # Run FSM Line Tracking with Node Turn behavior
    # Actions: "STRAIGHT", "LEFT", "RIGHT"
    run_agv_line_following(speed=1000, node_action="LEFT")
    #manual_move_robot()
    #move_front()
   
