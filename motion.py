from machine import Pin, PWM

class MecanumDriver:
    # Class constants for raw bit directional configurations
    FORWARD = 163
    BACKWARD = 92
    STRAFE_LEFT = 106
    STRAFE_RIGHT = 149
    STOP = 0

    def __init__(self, pwm1_pin=19, pwm2_pin=23, shcp_pin=18, en_pin=16, data_pin=5, stcp_pin=17):
        """ Initializes all motor control hardware resources """
        self.pwm1 = PWM(Pin(pwm1_pin))
        self.pwm2 = PWM(Pin(pwm2_pin))
        self.shcp = Pin(shcp_pin, Pin.OUT)
        self.en = Pin(en_pin, Pin.OUT)
        self.data = Pin(data_pin, Pin.OUT)
        self.stcp = Pin(stcp_pin, Pin.OUT)

        # Set base operational frequences
        self.pwm1.freq(500)
        self.pwm2.freq(500)

        #

    def set_speed(self, speed_value):
        """ Sets the duty cycle for motor speed (Accepts 0-1023)"""

        # We make sure the value stays within safe hardware limits
        speed_value = max(0, min(1023, speed_value))
        self.pwm1.duty(speed_value)
        self.pwm2.duty(speed_value)

    def _shift_out(self, value):
        """ Interal helper method to handle shift register bit steams """

        self.stcp.off()
        for i in range(8):
            bit = (value >> (7 - i)) & 1            # extracts the value of a single biy from a byte at a specific position, moving from left to right
            if bit == 1:
                self.data.on()
            else:
                self.data.off()
            self.shcp.on()
            self.shcp.off()
        self.stcp.on()

    def drive(self, direction_bit, speed=1000):
        """ High-level command to move the AGV chassis """

        self.set_speed(speed)
        self._shift_out(direction_bit)

    def halt(self):
        """ Immediate stoppin routine """
        self._shift_out(self.STOP)
        self.set_speed(0)
    
    def drive_strafe_correct(self, left_speed, right_speed, error_threshold=400, error=0):
        """Drives forward with differential speeds, shifting to strafe mode on sharp drift."""
        
        if error > error_threshold:
            self._shift_out(self.STRAFE_LEFT)
        
        elif error < -error_threshold:
            self._shift_out(self.STRAFE_RIGHT)
        
        else:
            self._shift_out(self.FORWARD)
        
        self.pwm1.duty(max(0, min(1023, int(left_speed))))
        self.pwm2.duty(max(0, min(1023, int(right_speed))))
