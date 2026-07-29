import time
import socket
import machine
from machine import Pin
import libs.motion
import libs.telemetry
import libs.leds

robot_driver = libs.motion.MecanumDriver()


# Power Saving & Helper functions
def apply_power_saving():
    """ Shuts down high-current systems dynamically to preserve battery"""
    print("\n[POWER] Movement finished. Activating automated standby idle..")
    robot_driver.halt()
    Pin(16, Pin.OUT).on()
    
    # start blinkinb our indicator in the background cleanly
    libs.leds.start_blink_indicator()
    print("[POWER] Motor driver suspended. Background heartbeat indicator active.\n")
def wake_up_systems():
    """ Wakes up motor driver hardware and stops idle indicators """
    libs.leds.stop_blink_indicator()
    Pin(16, Pin.OUT).off()
    print("[POWER] Systems awake. Ready for locomotion..")
    
# ==========================================
# 1. HELPER FUNCTIONS (Defined first!)
# ==========================================
def parse_network_command(raw_data):
    """
    Parses an incoming raw network string.
    Expects formats like: "FORWARD", "FORWARD:750" or "STOP"
    Returns: (command_string, speed_integer_or_None)
    """
    try:
        # FIXED: Added quotes around 'utf-8'
        clean_string = raw_data.decode('utf-8').strip().upper()
        
        if not clean_string:
            return None, None
        
        if ":" in clean_string:
            parts = clean_string.split(":", 1)
            command = parts[0]
            
            try:
                speed = int(parts[1])
                speed = max(0, min(1023, speed))
            except ValueError:
                print(f"[PARSER WARN] Invalid speed value '{parts[1]}'. Defaulting to 512.")
                speed = 512
            
            return command, speed
        else:
            return clean_string, None
        
    except Exception as e:
        print(f"[PARSER ERROR] Failed to parse data: {e}")
        return None, None

def manual_move_robot():
    robot_driver = libs.motion.MecanumDriver()
    libs.leds.stop_blink_indicator()
    Pin(16, Pin.OUT).off()
    
    """Diagnostic manual routine"""
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


# ==========================================
# 2. HARDWARE & NETWORK INITIALIZATION
# ==========================================
def wifi_connection():
    WIFI_SSID = "Mukwasi 2G"
    WIFI_PASS = "Mukwasi123"

    wifi = libs.telemetry.WifiEngine(WIFI_SSID, WIFI_PASS)
    

    if not wifi.connect():
        print("[ERROR] Could not connect to network. Exiting.")
        raise SystemExit

    # Open a TCP Socket Server on Port 8080
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8080))
    server_socket.listen(1)
    print("\n[SERVER] Listening for wireless commands on port 8080...")

    # ==========================================
    # 3. MAIN RUNTIME LOOP
    # ==========================================
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"\n[SERVER] Connection established from: {client_address}")
            
            wake_up_systems()
            
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break  # Client disconnected
                
                # INTEGRATED: Utilize the parser function here
                command, speed = parse_network_command(data)
                
                if not command:
                    continue
                    
                print(f"[EXECUTE] Command: {command} | Speed Override: {speed}")
                
                # Process parsed commands with flexible speeds
                if command == "FORWARD":
                    target_speed = speed if speed is not None else 512
                    robot_driver.drive(robot_driver.FORWARD, speed=target_speed)
                    time.sleep(3)
                    robot_driver.halt()
                elif command == "BACKWARD":
                    target_speed = speed if speed is not None else 512
                    robot_driver.drive(robot_driver.BACKWARD, speed=target_speed)
                    time.sleep(3)
                    robot_driver.halt()
                elif command == "LEFT":
                    target_speed = speed if speed is not None else 512
                    robot_driver.drive(robot_driver.STRAFE_LEFT, speed=target_speed)
                    time.sleep(3)
                    robot_driver.halt()
                elif command == "RIGHT":
                    target_speed = speed if speed is not None else 512
                    robot_driver.drive(robot_driver.STRAFE_RIGHT, speed=target_speed)
                    time.sleep(3)
                    robot_driver.halt()
                elif command == "STOP":
                    robot_driver.halt()
                    
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
    
    manual_move_robot()
    wifi_connection()
