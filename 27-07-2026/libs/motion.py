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

        self.pwm1.freq(500)
        self.pwm2.freq(500)

        # Active LOW enable
        self.enable_driver()
        self.halt()

    def enable_driver(self):
        """ Enables power stage on shield """
        self.en.off()

    def disable_driver(self):
        """ Disables power stage to save energy """
        self.en.on()

    def set_speed(self, speed_value):
        """ Sets the duty cycle for motor speed (Accepts 0-1023)"""
        speed_value = max(0, min(1023, int(speed_value)))
        self.pwm1.duty(speed_value)
        self.pwm2.duty(speed_value)

    def _shift_out(self, value):
        """ Internal helper method to handle shift register bit streams """
        self.stcp.off()
        for i in range(8):
            bit = (value >> (7 - i)) & 1
            if bit == 1:
                self.data.on()
            else:
                self.data.off()
            self.shcp.on()
            self.shcp.off()
        self.stcp.on()

    def drive(self, direction_bit, speed=450):
        """ High-level command to move the AGV chassis """
        self.enable_driver()
        self._shift_out(direction_bit)
        self.set_speed(speed)

    def halt(self):
        """ Immediate stopping routine """
        self.set_speed(0)
        self._shift_out(self.STOP)
