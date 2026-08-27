from machine import Pin, Timer, PWM


left_pwm = PWM(Pin(2), freq=1000)
right_pwm = PWM(Pin(12), freq=1000)

LOW_BRIGHTNESS = 3276
OFF = 0

blink_timer = Timer(0)

def _toggle_leds(timer_object):
    """ Internal callback function that flips the LED states automatically"""
    # check current state of left led (if duty>0, it is currently on)
    if left_pwm.duty_u16() > 0:
        left_pwm.duty_u16(OFF)
        right_pwm.duty_u16(LOW_BRIGHTNESS)
    else:
        left_pwm.duty_u16(LOW_BRIGHTNESS)
        right_pwm.duty_u16(OFF)

def start_blink_indicator():
    """ Starts blinking the status Leds in the background every 1 second """

    left_pwm.duty_u16(LOW_BRIGHTNESS)
    right_pwm.duty_u16(OFF)
    
    blink_timer.init(period=1000, mode=Timer.PERIODIC, callback=_toggle_leds)
    
    
def stop_blink_indicator():
    """ Turns off the background timer and forces LEDs off"""
    blink_timer.deinit()
    left_pwm.duty_u16(OFF)
    right_pwm.duty_u16(OFF)

