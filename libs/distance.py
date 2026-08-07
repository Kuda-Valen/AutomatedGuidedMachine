import time
from machine import Pin, ADC

class IRDistanceSensor:
    def __init__(self, pin_num=34, history_size=5):
        """
        Initializes an analog IR distance sensor on an ESP32 ADC pin.
        """
        self.adc = ADC(Pin(pin_num))
        self.adc.atten(ADC.ATTN_11DB)  # 0 - 3.3V range (0-4095)
        self.history_size = history_size
        self.history = [4000.0] * history_size  # Default safe distance memory

    def read_raw(self):
        """Returns raw ADC reading (0-4095)."""
        return self.adc.read()

    def read_cm(self):
        """
        Reads raw value, converts to approximate CM, and applies a median filter.
        IR sensors return HIGHER values when objects are CLOSER.
        """
        raw = self.read_raw()
        
        # Approximate distance formula for typical analog IR distance sensors
        # Adjust constants if using a digital threshold module
        if raw < 300:
            distance_cm = 80.0  # Far/Safe
        else:
            # Empirical inverse estimation curve for standard IR distance modules
            distance_cm = (27000.0 / (raw - 200.0))
            distance_cm = max(2.0, min(80.0, distance_cm))
            
        # Apply Moving Median Filter
        self.history.append(distance_cm)
        self.history = self.history[-self.history_size:]
        
        sorted_history = sorted(self.history)
        median_cm = sorted_history[len(sorted_history) // 2]
        return median_cm
