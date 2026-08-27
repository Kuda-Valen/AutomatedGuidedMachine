import time
from machine import Pin, ADC

class LineSensors3Pin:
    def __init__(self, pin_left=35, pin_mid=36, pin_right=39, threshold=2000):
        self.adc_l = ADC(Pin(pin_left))
        self.adc_m = ADC(Pin(pin_mid))
        self.adc_r = ADC(Pin(pin_right))
        
        self.adc_l.atten(ADC.ATTN_11DB)
        self.adc_m.atten(ADC.ATTN_11DB)
        self.adc_r.atten(ADC.ATTN_11DB)
        
        self.threshold = threshold
        self.last_position = 2000

    def read_raw(self):
        return self.adc_l.read(), self.adc_m.read(), self.adc_r.read()

    def get_position(self):
        l, m, r = self.read_raw()
        
        l_active = l if l > self.threshold else 0
        m_active = m if m > self.threshold else 0
        r_active = r if r > self.threshold else 0
        
        total = l_active + m_active + r_active
        
        # Returns (position, line_detected)
        if total == 0:
            return self.last_position, False
            
        position = ((1000 * l_active) + (2000 * m_active) + (3000 * r_active)) / total
        self.last_position = position
        return position, True
