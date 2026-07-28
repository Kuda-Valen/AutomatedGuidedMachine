import network
import time

class WifiEngine:
    def __init__(self, ssid, password):
        """ Initializes the station interface resources """

        self.ssid = ssid
        self.password = password

        self.wlan = network.WLAN(network.STA_IF)

    def connect(self, timeout_seconds=15):
        """ Activates the radio and establishes a local connection network"""

        self.wlan.active(True)

        if not self.wlan.isconected():
            print(f"[WIFI] Connecting to network: {self.ssid}...")
            self.wlan.connect(self.ssid, self.password)

            # Non-blocking wait cycle with a safe timeout
            start_time = time.time()
            while not self.wlan.isconnected():
                if time.time() - start_time > timeout_seconds:
                    print("[WIFI] Connection attempt time out.")
                    return False
                time.sleep(0.5)

        # Connection successful
        ip_info = self.wlan.ifconfig()
        print(f"[WIFI] Connected Successfully! IP Address: {ip_info[0]}")
        return True

    def disconnect(self):
        """ Safely deactivates the radio to conserve battery power """

        if self.wlan.isconnected():
            self.wlan.disconnect()
        self.wlan.active(False)
        print("[WIFI] Network interface deactivated (Power Saved) ")

    def get_status(self):
        """ Returns the current connectoin state """
        return self.wlan.isconnected()
