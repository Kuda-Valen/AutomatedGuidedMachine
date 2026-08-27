import time

class PIDController:
    def __init__(self, kp=0.25, ki=0.0, kd=0.02, output_limits=(-300, 300)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min_output, self.max_output = output_limits
        
        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = time.ticks_ms()
        self.filtered_derivative = 0.0

    def compute(self, current_error):
        now = time.ticks_ms()
        dt = time.ticks_diff(now, self.last_time) / 1000.0
        
        if dt <= 0.001:
            dt = 0.001

        # Proportional term
        p_term = self.kp * current_error

        # Integral term with anti-windup
        self.integral += current_error * dt
        i_term = self.ki * self.integral

        # Filtered Derivative term (Low-pass filter alpha = 0.7)
        raw_derivative = (current_error - self.last_error) / dt
        self.filtered_derivative = (0.7 * self.filtered_derivative) + (0.3 * raw_derivative)
        d_term = self.kd * self.filtered_derivative

        # Total Output Clamping
        output = p_term + i_term + d_term
        output = max(self.min_output, min(self.max_output, output))

        self.last_error = current_error
        self.last_time = now

        return output

    def reset(self):
        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = time.ticks_ms()
        self.filtered_derivative = 0.0
