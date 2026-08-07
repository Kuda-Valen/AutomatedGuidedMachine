import time

class PIDController:
    def __init__(self, kp=120.0, ki=0.0, kd=15.0, output_limits=(-300, 300)):
        """
        Discrete PID Controller designed for embedded systems.
        :param kp: Proportional multiplier
        :param ki: Integral multiplier
        :param kd: Derivative multiplier
        :param output_limits: Min and max bounds for correction value
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min_output, self.max_output = output_limits
        
        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()

    def compute(self, current_error):
        """Calculates steering correction based on delta time."""
        now = time.time()
        dt = now - self.last_time
        
        # Guard against division by zero if loop runs extremely fast
        if dt <= 0.0:
            dt = 0.001

        # 1. Proportional Term
        p_term = self.kp * current_error

        # 2. Integral Term (Accumulated error with anti-windup clamping)
        self.integral += current_error * dt
        i_term = self.ki * self.integral

        # 3. Derivative Term (Rate of change of error)
        derivative = (current_error - self.last_error) / dt
        d_term = self.kd * derivative

        # Total Unconstrained Output
        output = p_term + i_term + d_term

        # Clamp output to hardware motor constraints
        output = max(self.min_output, min(self.max_output, output))

        # Save state for next iteration
        self.last_error = current_error
        self.last_time = now

        return output

    def reset(self):
        """Clears memory state when restarting or changing modes."""
        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()
