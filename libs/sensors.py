import time
from machine import Pin, ADC

class LineSensors:
    def __init__(self, left_pin=34, right_pin=35, threshold=2000):
        """ Initializes the IR line sensors on ESP32 ADC pins."""
        
        self.adc_left = ADC(Pin(left_pin))
        self.adc_right = ADC(Pin(right_pin))
        
        self.adc_left.atten(ADC.ATTN_11DB)
        self.adc_right.atten(ADC.ATTN_11DB)
        
        # Midpoint threshold between WHITE and BLACK
        self.threshold = threshold
        
    def read_raw(self):
        """ This method returns raw ADC integer readings (0-4095) for (left, right)"""
        return self.adc_left.read(), self.adc_right.read()
    
    def read_digital(self):
        """ Converts raw ADC readings to boolean flags based on threshold
            Returns: (left_on_line, right_on_line)
            Assumming DARK/BLACK returns higher values than LIGHT/WHITE"""
        
        raw_l, raw_r = self.read_raw()
        #Returns True if on black line, False if on white surface
        return raw_l > self.threshold, raw_r > self.threshold
    
    def run_calibration(self, duration_sec=10):
        """Helper method to stream raw values to terminal for calibration.
           Place robot over white tape, then black tape while running."""
        
        print("\n--- STARTING IR SENSOR CALIBRATIN ---")
        print("Move sensors over WHITE paper and BLACK tape...")
        start_time = time.time()
        
        while time.time() - start_time < duration_sec:
            raw_l, raw_r = self.read_raw()
            avg = (raw_l + raw_r) // 2
            print(f"LEFT: {raw_l:<5} | RIGHT: {raw_r:<5} | AVG: {avg:<5}")
            time.sleep(0.2)
        
        print("--- CALIBRATION COMPLETE ---")